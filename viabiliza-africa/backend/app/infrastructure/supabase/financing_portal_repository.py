from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from supabase import Client

from app.domain.entities.financing_portal_ops import (
    FinancingDisbursement,
    FinancingDocument,
    FinancingPortalActivity,
)
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from app.domain.repositories.financing_portal_repository import (
    IFinancingActivityRepository,
    IFinancingDisbursementRepository,
    IFinancingDocumentRepository,
)
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _map_disbursement(row: dict) -> FinancingDisbursement:
    return FinancingDisbursement(
        id=UUID(row["id"]),
        financing_id=UUID(row["financing_id"]),
        requested_amount=Decimal(str(row["requested_amount"])),
        approved_amount=(
            Decimal(str(row["approved_amount"])) if row.get("approved_amount") is not None else None
        ),
        paid_amount=Decimal(str(row.get("paid_amount") or 0)),
        currency=row["currency"],
        status=row["status"],
        purpose=row.get("purpose"),
        requested_by=UUID(row["requested_by"]),
        reviewed_by=UUID(row["reviewed_by"]) if row.get("reviewed_by") else None,
        requested_at=_parse_dt(row["requested_at"]),
        decided_at=_parse_dt(row["decided_at"]) if row.get("decided_at") else None,
        paid_at=_parse_dt(row["paid_at"]) if row.get("paid_at") else None,
        notes=row.get("notes"),
        created_at=_parse_dt(row["created_at"]),
        updated_at=_parse_dt(row["updated_at"]),
    )


def _map_document(row: dict) -> FinancingDocument:
    return FinancingDocument(
        id=UUID(row["id"]),
        financing_id=UUID(row["financing_id"]),
        doc_type=row["doc_type"],
        title=row["title"],
        file_ref=row.get("file_ref"),
        validation_status=row["validation_status"],
        uploaded_by=UUID(row["uploaded_by"]),
        validated_by=UUID(row["validated_by"]) if row.get("validated_by") else None,
        validated_at=_parse_dt(row["validated_at"]) if row.get("validated_at") else None,
        notes=row.get("notes"),
        created_at=_parse_dt(row["created_at"]),
        updated_at=_parse_dt(row["updated_at"]),
    )


def _map_activity(row: dict) -> FinancingPortalActivity:
    return FinancingPortalActivity(
        id=UUID(row["id"]),
        bank_code=row["bank_code"],
        financing_id=UUID(row["financing_id"]) if row.get("financing_id") else None,
        project_id=UUID(row["project_id"]) if row.get("project_id") else None,
        actor_id=UUID(row["actor_id"]) if row.get("actor_id") else None,
        actor_name=row.get("actor_name"),
        action=row["action"],
        summary=row["summary"],
        metadata=row.get("metadata") or {},
        created_at=_parse_dt(row["created_at"]),
    )


class SupabaseFinancingDisbursementRepository(IFinancingDisbursementRepository):
    TABLE = "financing_disbursement"

    def __init__(self, client: Client) -> None:
        self._client = client

    def create(
        self,
        *,
        financing_id: UUID,
        requested_amount: Decimal,
        currency: str,
        purpose: str | None,
        requested_by: UUID,
    ) -> FinancingDisbursement:
        payload = {
            "financing_id": str(financing_id),
            "requested_amount": str(requested_amount),
            "currency": currency,
            "purpose": purpose,
            "requested_by": str(requested_by),
            "status": "requested",
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        if row is None:
            raise RuntimeError("Falha ao criar pedido de desembolso")
        return _map_disbursement(row)

    def find_by_id(self, disbursement_id: UUID) -> FinancingDisbursement | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("id", str(disbursement_id))
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return _map_disbursement(row) if row else None

    def list_by_financing(self, financing_id: UUID) -> list[FinancingDisbursement]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("financing_id", str(financing_id))
            .order("requested_at", desc=True)
            .execute()
        )
        return [_map_disbursement(r) for r in get_rows(response)]

    def list_by_financing_ids(self, financing_ids: list[UUID]) -> list[FinancingDisbursement]:
        if not financing_ids:
            return []
        ids = [str(i) for i in financing_ids]
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .in_("financing_id", ids)
            .order("requested_at", desc=True)
            .execute()
        )
        return [_map_disbursement(r) for r in get_rows(response)]

    def list_by_bank_financing_ids(
        self, financing_ids: list[UUID], *, status: str | None = None
    ) -> list[FinancingDisbursement]:
        if not financing_ids:
            return []
        ids = [str(i) for i in financing_ids]
        query = self._client.table(self.TABLE).select("*").in_("financing_id", ids)
        if status:
            query = query.eq("status", status)
        response = query.order("requested_at", desc=True).execute()
        return [_map_disbursement(r) for r in get_rows(response)]

    def update_status(
        self,
        disbursement_id: UUID,
        *,
        status: str,
        reviewed_by: UUID | None = None,
        approved_amount: Decimal | None = None,
        paid_amount: Decimal | None = None,
        notes: str | None = None,
    ) -> FinancingDisbursement:
        now = datetime.now(timezone.utc).isoformat()
        payload: dict = {"status": status}
        if reviewed_by:
            payload["reviewed_by"] = str(reviewed_by)
        if approved_amount is not None:
            payload["approved_amount"] = str(approved_amount)
        if paid_amount is not None:
            payload["paid_amount"] = str(paid_amount)
        if notes is not None:
            payload["notes"] = notes
        if status in ("approved", "rejected"):
            payload["decided_at"] = now
        if status == "paid":
            payload["paid_at"] = now
            payload["decided_at"] = payload.get("decided_at") or now
        if status == "under_review" and reviewed_by:
            payload["decided_at"] = None

        response = (
            self._client.table(self.TABLE).update(payload).eq("id", str(disbursement_id)).execute()
        )
        row = get_single_row(response)
        if row is None:
            raise EntityNotFoundError("Desembolso", str(disbursement_id))
        return _map_disbursement(row)

    def count_pending_by_financing(self, financing_id: UUID) -> int:
        response = (
            self._client.table(self.TABLE)
            .select("id", count="exact")
            .eq("financing_id", str(financing_id))
            .in_("status", ["requested", "under_review", "approved"])
            .execute()
        )
        return int(response.count or 0)


class SupabaseFinancingDocumentRepository(IFinancingDocumentRepository):
    TABLE = "financing_document"

    def __init__(self, client: Client) -> None:
        self._client = client

    def create(
        self,
        *,
        financing_id: UUID,
        doc_type: str,
        title: str,
        file_ref: str | None,
        uploaded_by: UUID,
    ) -> FinancingDocument:
        payload = {
            "financing_id": str(financing_id),
            "doc_type": doc_type,
            "title": title,
            "file_ref": file_ref,
            "uploaded_by": str(uploaded_by),
            "validation_status": "pending",
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        if row is None:
            raise RuntimeError("Falha ao registar documento")
        return _map_document(row)

    def find_by_id(self, document_id: UUID) -> FinancingDocument | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("id", str(document_id))
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return _map_document(row) if row else None

    def list_by_financing(self, financing_id: UUID) -> list[FinancingDocument]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("financing_id", str(financing_id))
            .order("created_at", desc=True)
            .execute()
        )
        return [_map_document(r) for r in get_rows(response)]

    def list_by_financing_ids(self, financing_ids: list[UUID]) -> list[FinancingDocument]:
        if not financing_ids:
            return []
        ids = [str(i) for i in financing_ids]
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .in_("financing_id", ids)
            .order("created_at", desc=True)
            .execute()
        )
        return [_map_document(r) for r in get_rows(response)]

    def update_validation(
        self,
        document_id: UUID,
        *,
        validation_status: str,
        validated_by: UUID,
        notes: str | None = None,
    ) -> FinancingDocument:
        payload = {
            "validation_status": validation_status,
            "validated_by": str(validated_by),
            "validated_at": datetime.now(timezone.utc).isoformat(),
        }
        if notes is not None:
            payload["notes"] = notes
        response = (
            self._client.table(self.TABLE).update(payload).eq("id", str(document_id)).execute()
        )
        row = get_single_row(response)
        if row is None:
            raise EntityNotFoundError("Documento", str(document_id))
        return _map_document(row)

    def count_pending_by_financing(self, financing_id: UUID) -> int:
        response = (
            self._client.table(self.TABLE)
            .select("id", count="exact")
            .eq("financing_id", str(financing_id))
            .eq("validation_status", "pending")
            .execute()
        )
        return int(response.count or 0)


class SupabaseFinancingActivityRepository(IFinancingActivityRepository):
    TABLE = "financing_portal_activity"

    def __init__(self, client: Client) -> None:
        self._client = client

    def append(
        self,
        *,
        bank_code: str,
        action: str,
        summary: str,
        financing_id: UUID | None = None,
        project_id: UUID | None = None,
        actor_id: UUID | None = None,
        actor_name: str | None = None,
        metadata: dict | None = None,
    ) -> FinancingPortalActivity:
        payload = {
            "bank_code": bank_code.lower(),
            "action": action,
            "summary": summary,
            "financing_id": str(financing_id) if financing_id else None,
            "project_id": str(project_id) if project_id else None,
            "actor_id": str(actor_id) if actor_id else None,
            "actor_name": actor_name,
            "metadata": metadata or {},
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        if row is None:
            raise RuntimeError("Falha ao registar actividade")
        return _map_activity(row)

    def list_by_bank(self, bank_code: str, *, limit: int = 50) -> list[FinancingPortalActivity]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("bank_code", bank_code.lower())
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [_map_activity(r) for r in get_rows(response)]

    def list_by_financing(self, financing_id: UUID, *, limit: int = 50) -> list[FinancingPortalActivity]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("financing_id", str(financing_id))
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [_map_activity(r) for r in get_rows(response)]
