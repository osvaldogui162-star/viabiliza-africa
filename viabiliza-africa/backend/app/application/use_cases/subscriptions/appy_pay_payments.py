from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.application.services.commercial_pricing_service import CommercialPricingService
from app.application.use_cases.subscriptions.public_plans import (
    PrepareCheckoutUseCase,
    SubscribeToPlanUseCase,
)
from app.domain.enums.subscription_status import SubscriptionStatus
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, ValidationError
from app.domain.repositories.admin_config_repository import ISubscriptionRepository
from app.domain.repositories.payment_repository import ISubscriptionPaymentRepository
from typing import TYPE_CHECKING

from app.infrastructure.payments.appy_pay_client import (
    AppyPayClient,
    AppyPayError,
    extract_charge_id,
    extract_error_message,
    extract_reference,
    extract_status,
    is_sandbox_gpo_phone,
    map_appypay_status,
)

if TYPE_CHECKING:
    from app.application.use_cases.erp_billing.erp_billing_use_cases import (
        IssueSubscriptionFiscalDocumentUseCase,
    )


class InitiateAppyPayPaymentUseCase:
    """Cria cobrança AppyPay (GPO ou Referência)."""

    def __init__(
        self,
        subscription_repository: ISubscriptionRepository,
        payment_repository: ISubscriptionPaymentRepository,
        appy_pay_client: AppyPayClient,
        commercial_pricing: CommercialPricingService,
        *,
        sandbox: bool = True,
        issue_fiscal_document_use_case: "IssueSubscriptionFiscalDocumentUseCase | None" = None,
    ) -> None:
        self._subs = subscription_repository
        self._payments = payment_repository
        self._appy = appy_pay_client
        self._sandbox = sandbox
        self._commercial = commercial_pricing
        self._checkout = PrepareCheckoutUseCase(subscription_repository, commercial_pricing)
        self._issue_fiscal = issue_fiscal_document_use_case

    def execute(
        self,
        *,
        user_id: UUID,
        plan_code: str,
        billing_cycle: str,
        payment_method: str,
        phone_number: str | None = None,
    ) -> dict:
        if payment_method not in ("gpo", "ref"):
            raise ValidationError("Método AppyPay inválido — use gpo ou ref")

        checkout = self._checkout.execute(
            plan_code=plan_code,
            billing_cycle=billing_cycle,
            currency="AOA",
        )
        plan = checkout["plan"]
        amount_data = checkout["amount"]
        total = Decimal(str(amount_data["total"]))

        if total <= 0:
            subscribe = SubscribeToPlanUseCase(self._subs, self._commercial)
            return {
                "free_plan": True,
                **subscribe.execute(
                    user_id=user_id,
                    plan_code=plan_code,
                    billing_cycle=billing_cycle,
                    currency="AOA",
                    payment_method=None,
                ),
            }

        if payment_method == "gpo" and not phone_number:
            raise ValidationError("Número Multicaixa Express é obrigatório")

        if payment_method == "gpo" and self._sandbox and not is_sandbox_gpo_phone(phone_number or ""):
            raise ValidationError(
                "Ambiente TST AppyPay: o Multicaixa Express só aceita números de teste. "
                "Use 244900000000 (sucesso), 244900000001 (saldo), 244900000002 (timeout) "
                "ou 244900000003 (rejeitado). Números reais não recebem notificação no sandbox."
            )

        merchant_tx = AppyPayClient.new_merchant_transaction_id()
        description = f"ViabilizA+ {plan['name']} ({billing_cycle})"

        payment = self._payments.create(
            user_id=user_id,
            plan_code=plan_code,
            billing_cycle=billing_cycle,
            amount=total,
            currency="AOA",
            payment_method=payment_method,
            merchant_transaction_id=merchant_tx,
            description=description,
            phone_number=phone_number,
        )

        try:
            if payment_method == "gpo":
                charge = self._appy.create_gpo_charge(
                    amount=total,
                    phone_number=phone_number or "",
                    merchant_transaction_id=merchant_tx,
                    description=description,
                )
            else:
                charge = self._appy.create_ref_charge(
                    amount=total,
                    merchant_transaction_id=merchant_tx,
                    description=description,
                )
        except AppyPayError as exc:
            self._payments.update_from_appypay(
                UUID(payment["id"]),
                status="failed",
                error_message=str(exc),
                raw_response={"error": str(exc), "payload": exc.payload},
            )
            raise ValidationError(str(exc)) from exc

        charge_id = extract_charge_id(charge)
        entity, reference = extract_reference(charge)
        appy_status = extract_status(charge)
        mapped = map_appypay_status(appy_status)
        error_message = extract_error_message(charge)

        payment = self._payments.update_from_appypay(
            UUID(payment["id"]),
            appypay_charge_id=charge_id,
            appypay_status=appy_status,
            status="failed" if mapped == "failed" else ("processing" if mapped == "paid" else mapped),
            reference_entity=entity,
            reference_number=reference,
            raw_response=charge,
            error_message=error_message or ("Pagamento recusado pelo Multicaixa Express" if mapped == "failed" else None),
        )

        if mapped == "paid":
            payment = self._activate_subscription(user_id, payment)

        return {
            "payment": payment,
            "checkout": checkout,
            "instructions": _payment_instructions(payment, sandbox=self._sandbox),
        }

    def _activate_subscription(self, user_id: UUID, payment: dict) -> dict:
        assign = SubscribeToPlanUseCase(self._subs, self._commercial)
        result = assign.execute(
            user_id=user_id,
            plan_code=payment["plan_code"],
            billing_cycle=payment["billing_cycle"],
            currency="AOA",
            payment_method=f"appy_{payment['payment_method']}",
            payment_verified=True,
        )
        subscription_id = result["subscription"]["id"]
        updated = self._payments.update_from_appypay(
            UUID(payment["id"]),
            status="paid",
            paid_at=datetime.now(timezone.utc),
            subscription_id=UUID(subscription_id),
        )
        if self._issue_fiscal:
            try:
                self._issue_fiscal.execute(user_id=user_id, payment_id=UUID(updated["id"]))
            except Exception:
                pass
        return updated


class PollAppyPayPaymentUseCase:
    def __init__(
        self,
        subscription_repository: ISubscriptionRepository,
        payment_repository: ISubscriptionPaymentRepository,
        appy_pay_client: AppyPayClient,
        commercial_pricing: CommercialPricingService,
        *,
        sandbox: bool = True,
        issue_fiscal_document_use_case: "IssueSubscriptionFiscalDocumentUseCase | None" = None,
    ) -> None:
        self._subs = subscription_repository
        self._payments = payment_repository
        self._appy = appy_pay_client
        self._sandbox = sandbox
        self._initiate = InitiateAppyPayPaymentUseCase(
            subscription_repository,
            payment_repository,
            appy_pay_client,
            commercial_pricing,
            sandbox=sandbox,
            issue_fiscal_document_use_case=issue_fiscal_document_use_case,
        )

    def execute(self, *, user_id: UUID, payment_id: UUID) -> dict:
        payment = self._payments.find_by_id(payment_id, user_id=user_id)
        if payment is None:
            raise EntityNotFoundError("Pagamento", str(payment_id))

        if payment["status"] == "paid":
            return {
                "payment": payment,
                "instructions": _payment_instructions(payment, sandbox=self._sandbox),
            }

        charge_id = payment.get("appypay_charge_id")
        if charge_id:
            try:
                charge = self._appy.get_charge(charge_id)
                appy_status = extract_status(charge)
                mapped = map_appypay_status(appy_status)
                entity, reference = extract_reference(charge)
                error_message = extract_error_message(charge)
                payment = self._payments.update_from_appypay(
                    UUID(payment["id"]),
                    appypay_status=appy_status,
                    status="failed" if mapped == "failed" else ("processing" if mapped == "paid" else mapped),
                    reference_entity=entity or payment.get("reference_entity"),
                    reference_number=reference or payment.get("reference_number"),
                    raw_response=charge,
                    error_message=error_message or payment.get("error_message"),
                )
                if mapped == "paid":
                    payment = self._initiate._activate_subscription(user_id, payment)
            except AppyPayError as exc:
                payment = self._payments.update_from_appypay(
                    UUID(payment["id"]),
                    error_message=str(exc),
                )

        return {
            "payment": payment,
            "instructions": _payment_instructions(payment, sandbox=self._sandbox),
        }


class MockAppyPayReferenceUseCase:
    """Sandbox — simula pagamento de referência."""

    def __init__(
        self,
        subscription_repository: ISubscriptionRepository,
        payment_repository: ISubscriptionPaymentRepository,
        appy_pay_client: AppyPayClient,
        commercial_pricing: CommercialPricingService,
        *,
        sandbox: bool = True,
        issue_fiscal_document_use_case: "IssueSubscriptionFiscalDocumentUseCase | None" = None,
    ) -> None:
        self._payments = payment_repository
        self._appy = appy_pay_client
        self._poll = PollAppyPayPaymentUseCase(
            subscription_repository,
            payment_repository,
            appy_pay_client,
            commercial_pricing,
            sandbox=sandbox,
            issue_fiscal_document_use_case=issue_fiscal_document_use_case,
        )

    def execute(self, *, user_id: UUID, payment_id: UUID) -> dict:
        payment = self._payments.find_by_id(payment_id, user_id=user_id)
        if payment is None:
            raise EntityNotFoundError("Pagamento", str(payment_id))
        if payment["payment_method"] != "ref":
            raise ValidationError("Simulação disponível apenas para pagamento por referência")
        entity = payment.get("reference_entity")
        reference = payment.get("reference_number")
        if not entity or not reference:
            raise ValidationError("Referência ainda não disponível")

        self._appy.mock_reference_payment(entity=entity, reference_number=reference)
        return self._poll.execute(user_id=user_id, payment_id=payment_id)


def _payment_instructions(payment: dict, *, sandbox: bool = True) -> dict:
    method = payment["payment_method"]
    if method == "gpo":
        sandbox_note = (
            " No ambiente TST, use o número de teste 244900000000 — o pagamento é aprovado "
            "automaticamente sem notificação na app real."
            if sandbox
            else ""
        )
        return {
            "type": "gpo",
            "title": "Confirme no Multicaixa Express",
            "message": (
                "Foi enviado um pedido de pagamento para o número indicado. "
                "Abra a app Multicaixa Express e confirme a transacção."
                f"{sandbox_note}"
            ),
            "phone_number": payment.get("phone_number"),
        }
    return {
        "type": "ref",
        "title": "Pague com Referência Multicaixa",
        "message": "Utilize a entidade e referência abaixo no Multicaixa, ATM ou Internet Banking.",
        "entity": payment.get("reference_entity"),
        "reference_number": payment.get("reference_number"),
    }
