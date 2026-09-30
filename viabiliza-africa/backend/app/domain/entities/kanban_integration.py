from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.enums.kanban_provider import KanbanProvider


@dataclass
class ProjectKanbanIntegration:
    id: UUID
    project_id: UUID
    provider: KanbanProvider
    external_board_id: str | None
    board_url: str | None
    list_map: dict[str, str]
    metadata: dict
    created_at: datetime
    updated_at: datetime

    def list_id_for_status(self, status: str) -> str | None:
        return self.list_map.get(status)

    def status_for_list_id(self, list_id: str) -> str | None:
        for status, lid in self.list_map.items():
            if lid == list_id:
                return status
        return None
