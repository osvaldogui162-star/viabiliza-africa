from datetime import datetime
from uuid import UUID

from supabase import Client

from app.domain.entities.audit_trail_entry import AuditTrailEntry
from app.domain.enums.audit_action import AuditAction
from app.domain.enums.audit_entity_type import AuditEntityType
from app.domain.repositories.audit_trail_repository import IAuditTrailRepository
from app.infrastructure.supabase.ingestion_mappers import map_audit_trail
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


class SupabaseAuditTrailRepository(IAuditTrailRepository):
    TABLE = "audit_trail"

    def __init__(self, client: Client) -> None:
        self._client = client

    def create(
        self,
        *,
        project_id: UUID,
        entity_type: AuditEntityType,
        entity_id: UUID,
        action: AuditAction,
        actor_id: UUID | None,
        data_hash: str,
        previous_hash: str | None = None,
        ip_address: str | None = None,
        metadata: dict | None = None,
    ) -> AuditTrailEntry:
        payload = {
            "project_id": str(project_id),
            "entity_type": entity_type.value,
            "entity_id": str(entity_id),
            "action": action.value,
            "actor_id": str(actor_id) if actor_id else None,
            "data_hash": data_hash,
            "previous_hash": previous_hash,
            "ip_address": ip_address,
            "metadata": metadata or {},
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        rows = get_rows(response)
        if not rows:
            raise RuntimeError("Falha ao registar audit trail")
        return map_audit_trail(rows[0])

    def find_by_project(
        self,
        project_id: UUID,
        *,
        entity_type: AuditEntityType | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditTrailEntry]:
        query = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("project_id", str(project_id))
        )
        if entity_type:
            query = query.eq("entity_type", entity_type.value)
        response = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        return [map_audit_trail(r) for r in get_rows(response)]

    def count_by_project(
        self,
        project_id: UUID,
        *,
        entity_type: AuditEntityType | None = None,
    ) -> int:
        query = (
            self._client.table(self.TABLE)
            .select("id", count="exact")
            .eq("project_id", str(project_id))
        )
        if entity_type:
            query = query.eq("entity_type", entity_type.value)
        response = query.execute()
        return response.count or 0

    def get_last_hash_for_entity(
        self, entity_type: AuditEntityType, entity_id: UUID
    ) -> str | None:
        response = (
            self._client.table(self.TABLE)
            .select("data_hash")
            .eq("entity_type", entity_type.value)
            .eq("entity_id", str(entity_id))
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return row["data_hash"] if row else None

    def _apply_global_filters(self, query, **filters):
        if filters.get("project_id"):
            query = query.eq("project_id", str(filters["project_id"]))
        if filters.get("actor_id"):
            query = query.eq("actor_id", str(filters["actor_id"]))
        if filters.get("entity_type"):
            query = query.eq("entity_type", filters["entity_type"].value)
        if filters.get("action"):
            query = query.eq("action", filters["action"].value)
        if filters.get("from_date"):
            query = query.gte("created_at", filters["from_date"].isoformat())
        if filters.get("to_date"):
            query = query.lte("created_at", filters["to_date"].isoformat())
        return query

    def find_global(
        self,
        *,
        project_id: UUID | None = None,
        actor_id: UUID | None = None,
        entity_type: AuditEntityType | None = None,
        action: AuditAction | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditTrailEntry]:
        query = self._client.table(self.TABLE).select("*")
        query = self._apply_global_filters(
            query,
            project_id=project_id,
            actor_id=actor_id,
            entity_type=entity_type,
            action=action,
            from_date=from_date,
            to_date=to_date,
        )
        response = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        return [map_audit_trail(r) for r in get_rows(response)]

    def count_global(
        self,
        *,
        project_id: UUID | None = None,
        actor_id: UUID | None = None,
        entity_type: AuditEntityType | None = None,
        action: AuditAction | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> int:
        query = self._client.table(self.TABLE).select("id", count="exact")
        query = self._apply_global_filters(
            query,
            project_id=project_id,
            actor_id=actor_id,
            entity_type=entity_type,
            action=action,
            from_date=from_date,
            to_date=to_date,
        )
        response = query.execute()
        return response.count or 0
