from datetime import datetime, timezone
from uuid import UUID

from supabase import Client

from app.domain.entities.billing_integration import ProjectBillingIntegration
from app.domain.repositories.billing_integration_repository import IProjectBillingIntegrationRepository
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _map(row: dict) -> ProjectBillingIntegration:
    return ProjectBillingIntegration(
        id=UUID(row["id"]),
        project_id=UUID(row["project_id"]),
        erp_label=row.get("erp_label"),
        connection_status=row["connection_status"],
        api_key_hint=row.get("api_key_hint"),
        api_key_hash=row.get("api_key_hash"),
        last_sync_at=_parse_dt(row.get("last_sync_at")),
        last_hash=row.get("last_hash"),
        latest_snapshot=row.get("latest_snapshot") or {},
        created_at=_parse_dt(row["created_at"]) or datetime.now(timezone.utc),
        updated_at=_parse_dt(row["updated_at"]) or datetime.now(timezone.utc),
    )


class SupabaseProjectBillingIntegrationRepository(IProjectBillingIntegrationRepository):
    def __init__(self, client: Client) -> None:
        self._db = client

    def find_by_project(self, project_id: UUID) -> ProjectBillingIntegration | None:
        row = get_single_row(
            self._db.table("project_billing_integration")
            .select("*")
            .eq("project_id", str(project_id))
            .limit(1)
        )
        return _map(row) if row else None

    def find_by_api_key_hash(self, api_key_hash: str) -> ProjectBillingIntegration | None:
        row = get_single_row(
            self._db.table("project_billing_integration")
            .select("*")
            .eq("api_key_hash", api_key_hash)
            .limit(1)
        )
        return _map(row) if row else None

    def find_by_projects(self, project_ids: list[UUID]) -> dict[UUID, ProjectBillingIntegration]:
        if not project_ids:
            return {}
        ids = [str(i) for i in project_ids]
        rows = get_rows(
            self._db.table("project_billing_integration").select("*").in_("project_id", ids)
        )
        return {UUID(r["project_id"]): _map(r) for r in rows}

    def upsert(
        self,
        *,
        project_id: UUID,
        erp_label: str | None = None,
        connection_status: str | None = None,
        api_key_hint: str | None = None,
        api_key_hash: str | None = None,
    ) -> ProjectBillingIntegration:
        existing = self.find_by_project(project_id)
        payload: dict = {"project_id": str(project_id)}
        if erp_label is not None:
            payload["erp_label"] = erp_label
        if connection_status is not None:
            payload["connection_status"] = connection_status
        if api_key_hint is not None:
            payload["api_key_hint"] = api_key_hint
        if api_key_hash is not None:
            payload["api_key_hash"] = api_key_hash

        if existing is None:
            payload.setdefault("connection_status", "integrating")
            row = get_single_row(
                self._db.table("project_billing_integration").insert(payload).select("*")
            )
        else:
            row = get_single_row(
                self._db.table("project_billing_integration")
                .update(payload)
                .eq("project_id", str(project_id))
                .select("*")
            )
        return _map(row)

    def record_sync(
        self,
        *,
        project_id: UUID,
        payload: dict,
        payload_hash: str,
        connection_status: str = "active",
    ) -> ProjectBillingIntegration:
        now = datetime.now(timezone.utc).isoformat()
        self._db.table("project_billing_sync_event").insert(
            {
                "project_id": str(project_id),
                "payload_hash": payload_hash,
                "payload": payload,
                "synced_at": now,
            }
        ).execute()

        existing = self.find_by_project(project_id)
        upsert_payload = {
            "project_id": str(project_id),
            "connection_status": connection_status,
            "last_sync_at": now,
            "last_hash": payload_hash,
            "latest_snapshot": payload,
        }
        if existing is None:
            row = get_single_row(
                self._db.table("project_billing_integration").insert(upsert_payload).select("*")
            )
        else:
            row = get_single_row(
                self._db.table("project_billing_integration")
                .update(upsert_payload)
                .eq("project_id", str(project_id))
                .select("*")
            )
        return _map(row)
