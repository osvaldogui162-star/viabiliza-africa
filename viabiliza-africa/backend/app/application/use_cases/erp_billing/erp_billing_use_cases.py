from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from app.application.services.erp_billing_entitlement import ErpBillingEntitlementService
from app.domain.catalog.erp_billing_provider_catalog import get_provider, list_providers_public
from app.domain.exceptions.domain_exceptions import ValidationError
from app.domain.repositories.erp_billing_repository import IAccountErpBillingRepository
from app.domain.repositories.payment_repository import ISubscriptionPaymentRepository
from app.domain.repositories.user_repository import IUserRepository
from app.infrastructure.erp.erp_billing_adapters import (
    ErpBillingAdapterError,
    issue_subscription_invoice,
    test_connection,
)

SECRET_CONFIG_KEYS = frozenset({"api_key", "auth_token", "auth_header"})


def _mask_config(config: dict) -> dict:
    out = dict(config or {})
    for key in list(out.keys()):
        if key in SECRET_CONFIG_KEYS and out[key]:
            raw = str(out[key])
            out[key] = f"••••{raw[-4:]}" if len(raw) > 4 else "••••"
    return out


def _connection_output(row: dict | None) -> dict | None:
    if not row:
        return None
    return {
        "provider_code": row.get("provider_code"),
        "connection_status": row.get("connection_status"),
        "auto_fiscal_on_payment": row.get("auto_fiscal_on_payment"),
        "config": _mask_config(row.get("config") or {}),
        "last_test_at": row.get("last_test_at"),
        "last_error": row.get("last_error"),
        "updated_at": row.get("updated_at"),
    }


def _fiscal_output(row: dict) -> dict:
    return {
        "id": row.get("id"),
        "payment_id": row.get("payment_id"),
        "provider_code": row.get("provider_code"),
        "status": row.get("status"),
        "external_ref": row.get("external_ref"),
        "document_payload": row.get("document_payload") or {},
        "has_agt_export": bool(row.get("agt_export_xml")),
        "error_message": row.get("error_message"),
        "issued_at": row.get("issued_at"),
        "created_at": row.get("created_at"),
    }


class ListErpBillingProvidersUseCase:
    def execute(self) -> dict:
        return {"items": list_providers_public(), "total": len(list_providers_public())}


class GetAccountErpBillingUseCase:
    def __init__(
        self,
        erp_repo: IAccountErpBillingRepository,
        entitlement: ErpBillingEntitlementService,
    ) -> None:
        self._erp = erp_repo
        self._entitlement = entitlement

    def execute(self, *, user) -> dict:
        self._entitlement.ensure_can_use_erp_billing(user)
        conn = self._erp.get_connection(user.id)
        docs = self._erp.list_fiscal_documents(user.id, limit=10)
        return {
            "connection": _connection_output(conn),
            "fiscal_documents": [_fiscal_output(d) for d in docs],
        }


class SaveAccountErpBillingUseCase:
    def __init__(
        self,
        erp_repo: IAccountErpBillingRepository,
        entitlement: ErpBillingEntitlementService,
    ) -> None:
        self._erp = erp_repo
        self._entitlement = entitlement

    def execute(
        self,
        *,
        user,
        provider_code: str,
        config: dict,
        auto_fiscal_on_payment: bool = True,
    ) -> dict:
        self._entitlement.ensure_can_use_erp_billing(user)
        provider = get_provider(provider_code)
        if not provider:
            raise ValidationError("Fornecedor ERP inválido")
        if not self._entitlement.can_auto_fiscal_on_payment(user.id):
            auto_fiscal_on_payment = False
        merged = dict(config or {})
        existing = self._erp.get_connection(user.id)
        if existing and existing.get("provider_code") == provider_code.strip().lower():
            old_cfg = existing.get("config") or {}
            for key in SECRET_CONFIG_KEYS:
                val = merged.get(key)
                if isinstance(val, str) and val.startswith("••••"):
                    merged[key] = old_cfg.get(key)
        row = self._erp.upsert_connection(
            user.id,
            provider_code=provider["code"],
            config=merged,
            auto_fiscal_on_payment=auto_fiscal_on_payment,
            connection_status="configuring",
            last_error=None,
        )
        return {"connection": _connection_output(row)}


class TestAccountErpBillingUseCase:
    def __init__(
        self,
        erp_repo: IAccountErpBillingRepository,
        entitlement: ErpBillingEntitlementService,
    ) -> None:
        self._erp = erp_repo
        self._entitlement = entitlement

    def execute(self, *, user, provider_code: str | None = None, config: dict | None = None) -> dict:
        self._entitlement.ensure_can_use_erp_billing(user)
        row = self._erp.get_connection(user.id)
        code = (provider_code or (row or {}).get("provider_code") or "").strip().lower()
        cfg = config if config is not None else ((row or {}).get("config") or {})
        if not code:
            raise ValidationError("Seleccione um fornecedor ERP")
        try:
            test_connection(code, cfg)
            now = datetime.now(timezone.utc)
            updated = self._erp.update_connection_status(
                user.id,
                connection_status="connected",
                last_test_at=now,
                last_error=None,
            )
            if config is not None and provider_code:
                updated = self._erp.upsert_connection(
                    user.id,
                    provider_code=code,
                    config=cfg,
                    auto_fiscal_on_payment=bool((row or {}).get("auto_fiscal_on_payment", True)),
                    connection_status="connected",
                )
            return {"ok": True, "connection": _connection_output(updated)}
        except ErpBillingAdapterError as exc:
            self._erp.update_connection_status(
                user.id,
                connection_status="error",
                last_error=str(exc),
            )
            raise ValidationError(str(exc)) from exc


class IssueSubscriptionFiscalDocumentUseCase:
    """Emite documento fiscal após pagamento AppyPay (se ERP configurado)."""

    def __init__(
        self,
        erp_repo: IAccountErpBillingRepository,
        payment_repo: ISubscriptionPaymentRepository,
        user_repo: IUserRepository,
        entitlement: ErpBillingEntitlementService,
    ) -> None:
        self._erp = erp_repo
        self._payments = payment_repo
        self._users = user_repo
        self._entitlement = entitlement

    def execute(self, *, user_id: UUID, payment_id: UUID) -> dict | None:
        existing = self._erp.find_fiscal_by_payment(payment_id)
        if existing:
            return _fiscal_output(existing)

        payment = self._payments.find_by_id(payment_id, user_id=user_id)
        if not payment or payment.get("status") != "paid":
            return None

        user = self._users.find_by_id(user_id)
        if not user:
            return None

        try:
            self._entitlement.ensure_can_use_erp_billing(user)
        except ValidationError:
            doc = self._erp.create_fiscal_document(
                user_id=user_id,
                payment_id=payment_id,
                provider_code="none",
                status="skipped",
                error_message="Plano ou pagamento não elegível para ERP",
            )
            return _fiscal_output(doc)

        conn = self._erp.get_connection(user_id)
        if not conn or conn.get("connection_status") != "connected":
            doc = self._erp.create_fiscal_document(
                user_id=user_id,
                payment_id=payment_id,
                provider_code=(conn or {}).get("provider_code") or "none",
                status="skipped",
                error_message="ERP não configurado ou ligação inactiva",
            )
            return _fiscal_output(doc)

        if not conn.get("auto_fiscal_on_payment"):
            doc = self._erp.create_fiscal_document(
                user_id=user_id,
                payment_id=payment_id,
                provider_code=conn["provider_code"],
                status="skipped",
                error_message="Emissão automática desactivada",
            )
            return _fiscal_output(doc)

        if not self._entitlement.can_auto_fiscal_on_payment(user_id):
            doc = self._erp.create_fiscal_document(
                user_id=user_id,
                payment_id=payment_id,
                provider_code=conn["provider_code"],
                status="skipped",
                error_message="Plano Starter — emissão manual; use export AGT ou actualize para Business",
            )
            return _fiscal_output(doc)

        invoice = {
            "reference": payment.get("merchant_transaction_id"),
            "amount": payment.get("amount"),
            "currency": payment.get("currency") or "AOA",
            "description": payment.get("description") or f"Plano {payment.get('plan_code')}",
            "customer_name": user.full_name,
            "customer_email": user.email,
            "plan_code": payment.get("plan_code"),
            "billing_cycle": payment.get("billing_cycle"),
        }
        cfg = conn.get("config") or {}
        provider_code = conn["provider_code"]
        try:
            result = issue_subscription_invoice(provider_code, cfg, invoice=invoice)
            status = result.get("status_hint") or "issued"
            if status == "export_ready":
                final_status = "export_ready"
            else:
                final_status = "issued"
            doc = self._erp.create_fiscal_document(
                user_id=user_id,
                payment_id=payment_id,
                provider_code=provider_code,
                status=final_status,
                external_ref=result.get("external_ref"),
                document_payload=result.get("document_payload") or {},
                agt_export_xml=result.get("agt_export_xml"),
                issued_at=datetime.now(timezone.utc),
            )
            return _fiscal_output(doc)
        except ErpBillingAdapterError as exc:
            doc = self._erp.create_fiscal_document(
                user_id=user_id,
                payment_id=payment_id,
                provider_code=provider_code,
                status="failed",
                error_message=str(exc),
            )
            return _fiscal_output(doc)


class GetSubscriptionFiscalDocumentExportUseCase:
    def __init__(self, erp_repo: IAccountErpBillingRepository, entitlement: ErpBillingEntitlementService) -> None:
        self._erp = erp_repo
        self._entitlement = entitlement

    def execute(self, *, user, document_id: UUID) -> dict:
        self._entitlement.ensure_can_use_erp_billing(user)
        row = self._erp.get_fiscal_document(user.id, document_id)
        if not row:
            raise ValidationError("Documento fiscal não encontrado")
        if not row.get("agt_export_xml"):
            raise ValidationError("Este documento não inclui export AGT")
        return {
            "id": row["id"],
            "agt_export_xml": row["agt_export_xml"],
            "filename": f"agt-export-{row['id']}.xml",
        }
