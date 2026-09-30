from uuid import UUID

from app.application.interfaces.kanban_provider import ExternalKanbanBoard, IKanbanProvider
from app.config import Config
from app.domain.entities.kanban_integration import ProjectKanbanIntegration
from app.domain.entities.project import Project
from app.domain.enums.kanban_provider import KanbanProvider
from app.domain.repositories.kanban_integration_repository import IKanbanIntegrationRepository


class KanbanBoardService:
    """Garante board Kanban externo por projeto e expõe metadados de integração."""

    def __init__(
        self,
        config: Config,
        integration_repository: IKanbanIntegrationRepository,
        trello_provider: IKanbanProvider | None,
    ) -> None:
        self._config = config
        self._integrations = integration_repository
        self._trello = trello_provider

    @property
    def active_provider(self) -> KanbanProvider:
        raw = self._config.KANBAN_PROVIDER.lower()
        if KanbanProvider.is_valid(raw):
            return KanbanProvider(raw)
        return KanbanProvider.LOCAL

    def is_external_enabled(self) -> bool:
        return self.active_provider == KanbanProvider.TRELLO and self._trello is not None

    def ensure_board(self, project: Project) -> ProjectKanbanIntegration | None:
        if not self.is_external_enabled():
            return self._integrations.find_by_project(project.id)

        existing = self._integrations.find_by_project(project.id)
        if existing and existing.external_board_id:
            return existing

        assert self._trello is not None
        board_name = f"ViabilizA+ | {project.name}"[:163]
        external = self._trello.create_board(board_name)
        return self._integrations.upsert(
            project_id=project.id,
            provider=KanbanProvider.TRELLO,
            external_board_id=external.external_board_id,
            board_url=external.board_url,
            list_map=external.list_map,
            metadata=external.metadata,
        )

    def to_external_board(self, integration: ProjectKanbanIntegration) -> ExternalKanbanBoard:
        return ExternalKanbanBoard(
            external_board_id=integration.external_board_id or "",
            board_url=integration.board_url or "",
            list_map=integration.list_map,
            metadata=integration.metadata,
        )

    def get_integration(self, project_id: UUID) -> ProjectKanbanIntegration | None:
        return self._integrations.find_by_project(project_id)
