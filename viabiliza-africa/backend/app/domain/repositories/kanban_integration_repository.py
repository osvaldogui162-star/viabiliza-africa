from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.kanban_integration import ProjectKanbanIntegration
from app.domain.enums.kanban_provider import KanbanProvider


class IKanbanIntegrationRepository(ABC):
    @abstractmethod
    def find_by_project(self, project_id: UUID) -> ProjectKanbanIntegration | None:
        ...

    @abstractmethod
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
        ...
