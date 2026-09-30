from uuid import UUID

from supabase import Client

from app.domain.entities.kanban_integration import ProjectKanbanIntegration
from app.domain.enums.kanban_provider import KanbanProvider
from app.domain.repositories.kanban_integration_repository import IKanbanIntegrationRepository
from app.infrastructure.supabase.response_helpers import get_single_row


def _map_row(row: dict) -> ProjectKanbanIntegration:
    from datetime import datetime

    return ProjectKanbanIntegration(
        id=UUID(row["id"]),
        project_id=UUID(row["project_id"]),
        provider=KanbanProvider(row["provider"]),
        external_board_id=row.get("external_board_id"),
        board_url=row.get("board_url"),
        list_map=row.get("list_map") or {},
        metadata=row.get("metadata") or {},
        created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
        updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00")),
    )


class SupabaseKanbanIntegrationRepository(IKanbanIntegrationRepository):
    TABLE = "project_kanban_integrations"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_by_project(self, project_id: UUID) -> ProjectKanbanIntegration | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("project_id", str(project_id))
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return _map_row(row) if row else None

    def upsert(
        self,
        *,
        project_id: UUID,
        provider: KanbanProvider,
        external_board_id: str | None,
        board_url: str | None,
        list_map: dict[str, str],
        metadata: dict | None = None,
    ) -> ProjectKanbanIntegration:
        payload = {
            "project_id": str(project_id),
            "provider": provider.value,
            "external_board_id": external_board_id,
            "board_url": board_url,
            "list_map": list_map,
            "metadata": metadata or {},
        }
        response = (
            self._client.table(self.TABLE)
            .upsert(payload, on_conflict="project_id")
            .execute()
        )
        row = get_single_row(response)
        return _map_row(row)
