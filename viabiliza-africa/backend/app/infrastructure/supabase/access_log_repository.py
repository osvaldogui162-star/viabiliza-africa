from datetime import datetime
from uuid import UUID

from supabase import Client

from app.domain.entities.access_log import AccessLog
from app.domain.enums.access_action import AccessAction
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.infrastructure.supabase.mappers import map_access_log_row
from app.infrastructure.supabase.response_helpers import get_rows


class SupabaseAccessLogRepository(IAccessLogRepository):
    """Implementação concreta do repositório de logs via Supabase."""

    TABLE = "access_logs"

    def __init__(self, client: Client) -> None:
        self._client = client

    def create(
        self,
        *,
        user_id: UUID | None,
        action: AccessAction,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict | None = None,
    ) -> AccessLog:
        payload = {
            "user_id": str(user_id) if user_id else None,
            "action": action.value,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "metadata": metadata or {},
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        rows = get_rows(response)
        if not rows:
            raise RuntimeError("Falha ao registar log de acesso")
        return map_access_log_row(rows[0])

    def find_all(
        self,
        *,
        user_id: UUID | None = None,
        action: AccessAction | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AccessLog]:
        query = self._client.table(self.TABLE).select("*")
        if user_id is not None:
            query = query.eq("user_id", str(user_id))
        if action is not None:
            query = query.eq("action", action.value)
        if from_date is not None:
            query = query.gte("created_at", from_date.isoformat())
        if to_date is not None:
            query = query.lte("created_at", to_date.isoformat())

        response = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        return [map_access_log_row(row) for row in get_rows(response)]

    def count(
        self,
        *,
        user_id: UUID | None = None,
        action: AccessAction | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> int:
        query = self._client.table(self.TABLE).select("id", count="exact")
        if user_id is not None:
            query = query.eq("user_id", str(user_id))
        if action is not None:
            query = query.eq("action", action.value)
        if from_date is not None:
            query = query.gte("created_at", from_date.isoformat())
        if to_date is not None:
            query = query.lte("created_at", to_date.isoformat())

        response = query.execute()
        return response.count or 0
