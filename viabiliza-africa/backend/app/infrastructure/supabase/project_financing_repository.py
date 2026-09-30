from datetime import datetime
from decimal import Decimal
from uuid import UUID

from supabase import Client

from app.domain.entities.project_financing import ProjectFinancing
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from app.domain.repositories.project_financing_repository import IProjectFinancingRepository
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


def _parse_dt(value: str):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _map_row(row: dict) -> ProjectFinancing:
    return ProjectFinancing(
        id=UUID(row["id"]),
        project_id=UUID(row["project_id"]),
        bank_code=row["bank_code"],
        submission_id=UUID(row["submission_id"]) if row.get("submission_id") else None,
        decision=row["decision"],
        workflow_status=row.get("workflow_status") or "active",
        approved_amount=Decimal(str(row["approved_amount"])),
        currency=row["currency"],
        interest_rate_pct=(
            Decimal(str(row["interest_rate_pct"])) if row.get("interest_rate_pct") is not None else None
        ),
        term_months=row.get("term_months"),
        disbursed_amount=Decimal(str(row.get("disbursed_amount") or 0)),
        monitoring_status=row["monitoring_status"],
        notes=row.get("notes"),
        submitted_by=UUID(row["submitted_by"]) if row.get("submitted_by") else None,
        decided_by=UUID(row["decided_by"]),
        decision_at=_parse_dt(row["decision_at"]),
        bank_decided_by=UUID(row["bank_decided_by"]) if row.get("bank_decided_by") else None,
        bank_decided_at=(
            _parse_dt(row["bank_decided_at"]) if row.get("bank_decided_at") else None
        ),
        is_active=row["is_active"],
        created_at=_parse_dt(row["created_at"]),
        updated_at=_parse_dt(row["updated_at"]),
    )


class SupabaseProjectFinancingRepository(IProjectFinancingRepository):
    TABLE = "project_financing"

    def __init__(self, client: Client) -> None:
        self._client = client

    def create(
        self,
        *,
        project_id: UUID,
        bank_code: str,
        submission_id: UUID | None,
        decision: str,
        workflow_status: str,
        approved_amount: Decimal,
        currency: str,
        interest_rate_pct: Decimal | None,
        term_months: int | None,
        disbursed_amount: Decimal,
        notes: str | None,
        submitted_by: UUID | None,
        decided_by: UUID,
    ) -> ProjectFinancing:
        payload = {
            "project_id": str(project_id),
            "bank_code": bank_code.lower(),
            "submission_id": str(submission_id) if submission_id else None,
            "decision": decision,
            "workflow_status": workflow_status,
            "approved_amount": str(approved_amount),
            "currency": currency,
            "interest_rate_pct": str(interest_rate_pct) if interest_rate_pct is not None else None,
            "term_months": term_months,
            "disbursed_amount": str(disbursed_amount),
            "notes": notes,
            "submitted_by": str(submitted_by) if submitted_by else None,
            "decided_by": str(decided_by),
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        if row is None:
            raise RuntimeError("Falha ao criar financiamento")
        return _map_row(row)

    def find_by_id(self, financing_id: UUID) -> ProjectFinancing | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("id", str(financing_id))
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return _map_row(row) if row else None

    def find_by_project(self, project_id: UUID, *, active_only: bool = True) -> list[ProjectFinancing]:
        query = self._client.table(self.TABLE).select("*").eq("project_id", str(project_id))
        if active_only:
            query = query.eq("is_active", True)
        response = query.order("decision_at", desc=True).execute()
        return [_map_row(row) for row in get_rows(response)]

    def list_by_bank(
        self,
        bank_code: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ProjectFinancing]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("bank_code", bank_code.lower())
            .eq("is_active", True)
            .eq("workflow_status", "active")
            .in_("decision", ["approved", "conditional"])
            .order("decision_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return [_map_row(row) for row in get_rows(response)]

    def list_pending_by_bank(
        self,
        bank_code: str,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProjectFinancing]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("bank_code", bank_code.lower())
            .eq("is_active", True)
            .eq("workflow_status", "pending_bank")
            .eq("decision", "pending")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return [_map_row(row) for row in get_rows(response)]

    def list_all_pending(self, *, limit: int = 100, offset: int = 0) -> list[ProjectFinancing]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("is_active", True)
            .eq("workflow_status", "pending_bank")
            .eq("decision", "pending")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return [_map_row(row) for row in get_rows(response)]

    def list_all_active(self, *, limit: int = 200, offset: int = 0) -> list[ProjectFinancing]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("is_active", True)
            .eq("workflow_status", "active")
            .in_("decision", ["approved", "conditional"])
            .order("decision_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return [_map_row(row) for row in get_rows(response)]

    def apply_bank_decision(
        self,
        financing_id: UUID,
        *,
        decision: str,
        workflow_status: str,
        approved_amount: Decimal,
        disbursed_amount: Decimal,
        interest_rate_pct: Decimal | None,
        term_months: int | None,
        notes: str | None,
        bank_decided_by: UUID,
        bank_decided_at: datetime,
        monitoring_status: str,
    ) -> ProjectFinancing:
        payload = {
            "decision": decision,
            "workflow_status": workflow_status,
            "approved_amount": str(approved_amount),
            "disbursed_amount": str(disbursed_amount),
            "interest_rate_pct": str(interest_rate_pct) if interest_rate_pct is not None else None,
            "term_months": term_months,
            "notes": notes,
            "bank_decided_by": str(bank_decided_by),
            "bank_decided_at": bank_decided_at.isoformat(),
            "decided_by": str(bank_decided_by),
            "decision_at": bank_decided_at.isoformat(),
            "monitoring_status": monitoring_status,
        }
        response = (
            self._client.table(self.TABLE)
            .update(payload)
            .eq("id", str(financing_id))
            .execute()
        )
        row = get_single_row(response)
        if row is None:
            raise EntityNotFoundError("Financiamento", str(financing_id))
        return _map_row(row)

    def update_monitoring_status(self, financing_id: UUID, status: str) -> ProjectFinancing:
        response = (
            self._client.table(self.TABLE)
            .update({"monitoring_status": status})
            .eq("id", str(financing_id))
            .execute()
        )
        row = get_single_row(response)
        if row is None:
            raise EntityNotFoundError("Financiamento", str(financing_id))
        return _map_row(row)

    def update_disbursed_amount(self, financing_id: UUID, amount: Decimal) -> ProjectFinancing:
        response = (
            self._client.table(self.TABLE)
            .update({"disbursed_amount": str(amount)})
            .eq("id", str(financing_id))
            .execute()
        )
        row = get_single_row(response)
        if row is None:
            raise EntityNotFoundError("Financiamento", str(financing_id))
        return _map_row(row)
