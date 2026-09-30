from datetime import date
from uuid import UUID

from app.application.interfaces.kanban_provider import IKanbanProvider
from app.application.services.kanban_board_service import KanbanBoardService
from app.domain.entities.collaboration import KanbanTask
from app.domain.entities.project import Project
from app.domain.enums.kanban_provider import KanbanProvider
from app.domain.enums.task_status import TaskStatus
from app.domain.repositories.collaboration_repository import IKanbanTaskRepository


class KanbanTaskService:
    """Sincroniza tarefas locais com o Kanban externo (Trello)."""

    def __init__(
        self,
        task_repository: IKanbanTaskRepository,
        board_service: KanbanBoardService,
        trello_provider: IKanbanProvider | None,
    ) -> None:
        self._tasks = task_repository
        self._boards = board_service
        self._trello = trello_provider

    def sync_from_external(self, project: Project, *, owner_id: UUID) -> int:
        """Importa/atualiza cartões do Trello para a base local."""
        if not self._boards.is_external_enabled() or self._trello is None:
            return 0

        integration = self._boards.ensure_board(project)
        if not integration or not integration.external_board_id:
            return 0

        board = self._boards.to_external_board(integration)
        external_cards = self._trello.list_cards(board)
        synced = 0

        for card in external_cards:
            local = self._tasks.find_by_external_id(project.id, card.external_id)
            if local:
                self._tasks.update(
                    local.id,
                    title=card.title,
                    description=card.description,
                    due_date=card.due_date,
                    status=card.status,
                    position=card.position,
                )
            else:
                self._tasks.create(
                    project_id=project.id,
                    title=card.title,
                    description=card.description,
                    assignee_id=None,
                    due_date=card.due_date,
                    status=card.status,
                    position=card.position,
                    created_by=owner_id,
                    external_id=card.external_id,
                    provider=KanbanProvider.TRELLO.value,
                )
            synced += 1

        return synced

    def create(
        self,
        project: Project,
        *,
        title: str,
        description: str | None,
        assignee_id: UUID | None,
        due_date: date | None,
        status: TaskStatus,
        position: int,
        created_by: UUID,
    ) -> KanbanTask:
        external_id = None
        provider = KanbanProvider.LOCAL.value

        if self._boards.is_external_enabled() and self._trello is not None:
            integration = self._boards.ensure_board(project)
            board = self._boards.to_external_board(integration)  # type: ignore[arg-type]
            card = self._trello.create_card(
                board,
                title=title,
                description=description,
                due_date=due_date,
                status=status,
                position=position,
            )
            external_id = card.external_id
            provider = KanbanProvider.TRELLO.value

        return self._tasks.create(
            project_id=project.id,
            title=title,
            description=description,
            assignee_id=assignee_id,
            due_date=due_date,
            status=status,
            position=position,
            created_by=created_by,
            external_id=external_id,
            provider=provider,
        )

    def update(
        self,
        project: Project,
        task: KanbanTask,
        *,
        title: str | None = None,
        description: str | None = None,
        assignee_id: UUID | None = ...,
        due_date: date | None = ...,
        status: TaskStatus | None = None,
        position: int | None = None,
    ) -> KanbanTask:
        if (
            task.external_id
            and task.provider == KanbanProvider.TRELLO.value
            and self._trello is not None
        ):
            integration = self._boards.ensure_board(project)
            if integration:
                board = self._boards.to_external_board(integration)
                self._trello.update_card(
                    board,
                    task.external_id,
                    title=title,
                    description=description,
                    due_date=due_date,
                    status=status or task.status,
                    position=position if position is not None else task.position,
                )

        return self._tasks.update(
            task.id,
            title=title,
            description=description,
            assignee_id=assignee_id,
            due_date=due_date,
            status=status,
            position=position,
        )

    def delete(self, project: Project, task: KanbanTask) -> None:
        if (
            task.external_id
            and task.provider == KanbanProvider.TRELLO.value
            and self._trello is not None
        ):
            self._trello.delete_card(task.external_id)
        self._tasks.delete(task.id)
