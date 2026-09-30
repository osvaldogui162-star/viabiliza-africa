from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.application.services.commercial_pricing_service import CommercialPricingService
from app.application.services.plan_capabilities import build_plan_capabilities
from app.application.services.subscription_service import SubscriptionService
from app.application.use_cases.admin.mappers import to_subscription_output
from app.domain.catalog.plan_commercial_pricing import (
    ONLINE_CHECKOUT_PLAN_CODES,
    PLAN_AOA_PRICING,
    PLAN_RECOMMENDATION,
    PUBLIC_PLAN_CODES,
)
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, ValidationError
from app.domain.enums.subscription_status import SubscriptionStatus
from app.domain.repositories.admin_config_repository import ISubscriptionRepository
from app.infrastructure.payments.appy_pay_client import appypay_checkout_meta

import os


def to_public_plan_output(plan, *, pricing: CommercialPricingService | None = None) -> dict:
    from app.application.use_cases.admin.mappers import to_plan_output

    data = to_plan_output(plan)
    features = plan.features or {}
    data["plan_tier"] = features.get("plan_tier", "main")
    data["popular"] = bool(features.get("popular"))
    data["contact_only"] = bool(features.get("contact_only"))
    data["yearly_only"] = bool(features.get("yearly_only"))
    data["emoji"] = features.get("emoji")
    data["support_sla"] = features.get("support_sla")
    data["hidden_from_pricing"] = bool(features.get("hidden_from_pricing"))
    data["billing_periods"] = features.get("billing_periods") or [
        "quarterly",
        "semiannual",
        "yearly",
    ]
    code = plan.code
    if code in PLAN_AOA_PRICING:
        for period in ("quarterly", "semiannual", "yearly"):
            entry = PLAN_AOA_PRICING[code][period]
            data[f"price_{period}_aoa"] = entry["fixed"]
            data[f"reference_{period}_aoa"] = entry["reference"]
    else:
        for key in (
            "price_quarterly_aoa",
            "price_semiannual_aoa",
            "price_yearly_aoa",
            "reference_quarterly_aoa",
            "reference_semiannual_aoa",
            "reference_yearly_aoa",
        ):
            if key in features:
                data[key] = features[key]
    rec = PLAN_RECOMMENDATION.get(code)
    if rec:
        data["recommendation"] = rec

    if pricing and code in PUBLIC_PLAN_CODES:
        promo = pricing.get_promotion_state()
        data["pricing_preview"] = {
            period: pricing.build_amount(code, period)
            for period in ("quarterly", "semiannual", "yearly")
        }
        data["promotion"] = promo
    return data


def _resolve_plan(pricing_repo: ISubscriptionRepository, code: str):
    normalized = code.strip().lower()
    plan = pricing_repo.find_plan_by_code(normalized)
    if plan is None or not plan.is_active:
        raise EntityNotFoundError("Plano", normalized)
    return plan


def _validate_billing_period(billing_cycle: str) -> str:
    if billing_cycle in ("monthly",):
        return "quarterly"
    if billing_cycle == "yearly":
        return "yearly"
    if billing_cycle not in ("quarterly", "semiannual", "yearly"):
        raise ValidationError(
            "Ciclo de faturação inválido — use quarterly, semiannual ou yearly"
        )
    return billing_cycle


class ListPublicPlansUseCase:
    """Listar planos activos para a página pública de preços."""

    def __init__(
        self,
        repository: ISubscriptionRepository,
        commercial_pricing: CommercialPricingService,
    ) -> None:
        self._repo = repository
        self._pricing = commercial_pricing

    def execute(self) -> dict:
        items = self._repo.find_all_plans(active_only=True)
        visible = [
            p
            for p in items
            if p.code in PUBLIC_PLAN_CODES
            and not (p.features or {}).get("hidden_from_pricing")
        ]
        visible.sort(key=lambda p: p.display_order)
        promotion = self._pricing.get_promotion_state()
        return {
            "items": [to_public_plan_output(p, pricing=self._pricing) for p in visible],
            "total": len(visible),
            "promotion": promotion,
            "billing_periods": [
                {"code": "quarterly", "label_pt": "Trimestral", "label_en": "Quarterly"},
                {"code": "semiannual", "label_pt": "Semestral", "label_en": "Semiannual"},
                {"code": "yearly", "label_pt": "Anual", "label_en": "Annual"},
            ],
        }


class GetMySubscriptionUseCase:
    """Estado da assinatura e utilização do utilizador autenticado."""

    def __init__(
        self,
        repository: ISubscriptionRepository,
        subscription_service: SubscriptionService,
        commercial_pricing: CommercialPricingService,
    ) -> None:
        self._repo = repository
        self._subs = subscription_service
        self._pricing = commercial_pricing

    def execute(self, *, user_id: UUID) -> dict:
        plan = self._subs.get_user_plan(user_id)
        subscription = self._repo.find_active_subscription(user_id)
        usage = self._subs.get_usage_snapshot(user_id)
        capabilities = build_plan_capabilities(plan)

        payload = {
            "plan": to_public_plan_output(plan, pricing=self._pricing),
            "subscription": to_subscription_output(subscription, plan) if subscription else None,
            "usage": usage,
            "capabilities": capabilities,
            "is_implicit_free": subscription is None and plan.code == "free",
            "promotion": self._pricing.get_promotion_state(),
        }
        return payload


class PrepareCheckoutUseCase:
    """Resumo de checkout antes do pagamento."""

    def __init__(
        self,
        repository: ISubscriptionRepository,
        commercial_pricing: CommercialPricingService,
    ) -> None:
        self._repo = repository
        self._pricing = commercial_pricing

    def execute(
        self,
        *,
        plan_code: str,
        billing_cycle: str = "quarterly",
        currency: str = "AOA",
    ) -> dict:
        code = plan_code.strip().lower()
        period = _validate_billing_period(billing_cycle)

        if code not in ONLINE_CHECKOUT_PLAN_CODES:
            plan = self._repo.find_plan_by_code(code)
            if plan and (plan.features or {}).get("contact_only"):
                raise ValidationError(
                    f"O plano «{plan.name}» requer contacto comercial. "
                    "Envie email para comercial@viabiliza.africa."
                )
            raise ValidationError(f"Plano «{code}» não disponível para subscrição online")

        if currency not in ("USD", "AOA"):
            raise ValidationError("Moeda inválida — pagamentos AppyPay usam AOA")

        plan = _resolve_plan(self._repo, code)
        amount = self._pricing.build_amount(code, period)
        recommendation = PLAN_RECOMMENDATION.get(code)

        return {
            "plan": to_public_plan_output(plan, pricing=self._pricing),
            "billing_cycle": period,
            "amount": amount,
            "recommendation": recommendation,
            "promotion": self._pricing.get_promotion_state(),
            "payment_methods": [
                {
                    "code": "gpo",
                    "label": "Multicaixa Express (AppyPay)",
                    "provider": "appypay",
                    "description": "Pagamento via número de telefone na app Multicaixa Express",
                },
                {
                    "code": "ref",
                    "label": "Referência Multicaixa (AppyPay)",
                    "provider": "appypay",
                    "description": "Entidade + referência para ATM, Multicaixa ou Internet Banking",
                },
            ],
            "payment_provider": "appypay",
            "currency_note": "Pagamentos processados em AOA via AppyPay (IVA 25%)",
            "appypay": appypay_checkout_meta(
                sandbox=os.getenv("APPYPAY_SANDBOX", "true").lower() == "true"
            ),
        }


class SubscribeToPlanUseCase:
    """Activar plano gratuito ou assinatura após pagamento verificado."""

    def __init__(
        self,
        repository: ISubscriptionRepository,
        commercial_pricing: CommercialPricingService,
    ) -> None:
        self._repo = repository
        self._pricing = commercial_pricing

    def execute(
        self,
        *,
        user_id: UUID,
        plan_code: str,
        billing_cycle: str = "quarterly",
        currency: str = "AOA",
        payment_method: str | None = None,
        payment_verified: bool = False,
    ) -> dict:
        code = plan_code.strip().lower()
        period = _validate_billing_period(billing_cycle)

        if code == "free":
            plan = _resolve_plan(self._repo, code)
            payment_verified = True
        elif code not in ONLINE_CHECKOUT_PLAN_CODES:
            plan = self._repo.find_plan_by_code(code)
            if plan and (plan.features or {}).get("contact_only"):
                raise ValidationError(
                    f"O plano «{plan.name}» requer contacto comercial. "
                    "Envie email para comercial@viabiliza.africa."
                )
            raise ValidationError(f"Plano «{code}» não disponível para subscrição online")
        else:
            plan = _resolve_plan(self._repo, code)

        if code != "free" and not payment_verified:
            raise ValidationError(
                "Planos pagos requerem pagamento confirmado via AppyPay. "
                "Utilize POST /api/v1/me/subscription/payments/appypay e aguarde confirmação."
            )

        amount = self._pricing.build_amount(code, period)

        ends_at = None
        if code != "free":
            now = datetime.now(timezone.utc)
            days = self._pricing.subscription_duration_days(period)
            ends_at = now + timedelta(days=days)

        sub = self._repo.assign_subscription(
            user_id=user_id,
            plan_id=plan.id,
            status=SubscriptionStatus.ACTIVE,
            ends_at=ends_at,
            created_by=user_id,
        )
        return {
            "message": f"Plano «{plan.name}» activado com sucesso",
            "subscription": to_subscription_output(sub, plan),
            "billing_cycle": period,
            "currency": currency,
            "payment_method": payment_method,
            "amount": amount,
            "reference": f"VA-{sub.id.hex[:8].upper()}",
        }
