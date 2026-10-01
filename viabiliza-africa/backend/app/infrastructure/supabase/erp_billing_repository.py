from datetime import datetime
from uuid import UUID

from supabase import Client

from app.domain.repositories.erp_billing_repository import IAccountErpBillingRepository


class SupabaseAccountErpBillingRepository(IAccountErpBillingRepository):
    def __init__(self, client: Client) -> None:
        self._db = client

    def get_connection(self, user_id: UUID) -> dict | None:
        res = (
            self._db.table("account_erp_billing_connections")
            .select("*")
            .eq("user_id", str(user_id))
            .limit(1)
            .execute()
        )
        rows = res.data or []
        return rows[0] if rows else None

    def upsert_connection(
        self,
        user_id: UUID,
        *,
        provider_code: str,
        config: dict,
        auto_fiscal_on_payment: bool,
        connection_status: str,
        last_error: str | None = None,
    ) -> dict:
        existing = self.get_connection(user_id)
        payload = {
            "user_id": str(user_id),
            "provider_code": provider_code,
            "config": config,
            "auto_fiscal_on_payment": auto_fiscal_on_payment,
            "connection_status": connection_status,
            "last_error": last_error,
        }
        if existing:
            res = (
                self._db.table("account_erp_billing_connections")
                .update(payload)
                .eq("user_id", str(user_id))
                .select("*")
                .execute()
            )
        else:
            res = self._db.table("account_erp_billing_connections").insert(payload).select("*").execute()
        rows = res.data or []
        if not rows:
            raise RuntimeError("Falha ao gravar ligação ERP")
        return rows[0]

    def update_connection_status(
        self,
        user_id: UUID,
        *,
        connection_status: str,
        last_test_at: datetime | None = None,
        last_error: str | None = None,
    ) -> dict | None:
        payload: dict = {"connection_status": connection_status, "last_error": last_error}
        if last_test_at is not None:
            payload["last_test_at"] = last_test_at.isoformat()
        res = (
            self._db.table("account_erp_billing_connections")
            .update(payload)
            .eq("user_id", str(user_id))
            .select("*")
            .execute()
        )
        rows = res.data or []
        return rows[0] if rows else None

    def create_fiscal_document(
        self,
        *,
        user_id: UUID,
        payment_id: UUID | None,
        provider_code: str,
        status: str,
        external_ref: str | None = None,
        document_payload: dict | None = None,
        agt_export_xml: str | None = None,
        error_message: str | None = None,
        issued_at: datetime | None = None,
    ) -> dict:
        payload = {
            "user_id": str(user_id),
            "payment_id": str(payment_id) if payment_id else None,
            "provider_code": provider_code,
            "status": status,
            "external_ref": external_ref,
            "document_payload": document_payload or {},
            "agt_export_xml": agt_export_xml,
            "error_message": error_message,
            "issued_at": issued_at.isoformat() if issued_at else None,
        }
        res = self._db.table("subscription_fiscal_documents").insert(payload).select("*").execute()
        rows = res.data or []
        if not rows:
            raise RuntimeError("Falha ao criar documento fiscal")
        return rows[0]

    def find_fiscal_by_payment(self, payment_id: UUID) -> dict | None:
        res = (
            self._db.table("subscription_fiscal_documents")
            .select("*")
            .eq("payment_id", str(payment_id))
            .limit(1)
            .execute()
        )
        rows = res.data or []
        return rows[0] if rows else None

    def list_fiscal_documents(self, user_id: UUID, *, limit: int = 20) -> list[dict]:
        res = (
            self._db.table("subscription_fiscal_documents")
            .select("*")
            .eq("user_id", str(user_id))
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return res.data or []

    def get_fiscal_document(self, user_id: UUID, document_id: UUID) -> dict | None:
        res = (
            self._db.table("subscription_fiscal_documents")
            .select("*")
            .eq("user_id", str(user_id))
            .eq("id", str(document_id))
            .limit(1)
            .execute()
        )
        rows = res.data or []
        return rows[0] if rows else None

    def user_has_paid_subscription_payment(self, user_id: UUID) -> bool:
        res = (
            self._db.table("subscription_payments")
            .select("id")
            .eq("user_id", str(user_id))
            .eq("status", "paid")
            .limit(1)
            .execute()
        )
        return bool(res.data)
