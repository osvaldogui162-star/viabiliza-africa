from datetime import date
from uuid import UUID

from app.application.services.collaboration_access_policy import CollaborationAccessPolicy
from app.application.services.kanban_board_service import KanbanBoardService
from app.application.services.kanban_task_service import KanbanTaskService
from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.services.task_dependency_validator import TaskDependencyValidator
from app.application.use_cases.collaboration.mappers import group_tasks_by_status, to_task_output
from app.domain.enums.task_status import TaskStatus
from app.domain.exceptions.domain_exceptions import (
    AuthorizationError,
    EntityNotFoundError,
    ValidationError,
)
from app.domain.repositories.collaboration_repository import IKanbanTaskRepository


class CreateTaskUseCase:
    """UC24 — Criar tarefa no Kanban (sincroniza com Trello se activo)."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        collaboration_policy: CollaborationAccessPolicy,
        task_repository: IKanbanTaskRepository,
        kanban_task_service: KanbanTaskService,
    ) -> None:
        self._ctx = context_resolver
        self._policy = collaboration_policy
        self._tasks = task_repository
        self._kanban = kanban_task_service

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        title: str,
        description: str | None = None,
        assignee_id: UUID | None = None,
        due_date: date | None = None,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_collaborate(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para criar tarefas neste projeto")

        title = title.strip()
        if not title:
            raise ValidationError("Título da tarefa é obrigatório")
        if len(title) > 200:
            raise ValidationError("Título não pode exceder 200 caracteres")

        self._policy.validate_assignee(ctx.project, assignee_id)

        position = self._tasks.max_position(project_id, TaskStatus.TODO) + 1
        task = self._kanban.create(
            ctx.project,
            title=title,
            description=description.strip() if description else None,
            assignee_id=assignee_id,
            due_date=due_date,
            status=TaskStatus.TODO,
            position=position,
            created_by=actor_id,
        )
        return to_task_output(task)


class ListTasksUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        collaboration_policy: CollaborationAccessPolicy,
        task_repository: IKanbanTaskRepository,
        kanban_task_service: KanbanTaskService,
        board_service: KanbanBoardService,
    ) -> None:
        self._ctx = context_resolver
        self._policy = collaboration_policy
        self._tasks = task_repository
        self._kanban = kanban_task_service
        self._boards = board_service

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        status: str | None = None,
        grouped: bool = True,
        sync: bool = True,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_collaborate(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para visualizar tarefas")

        if sync and self._boards.is_external_enabled():
            self._kanban.sync_from_external(ctx.project, owner_id=ctx.project.owner_id)

        parsed_status = None
        if status:
            if not TaskStatus.is_valid(status):
                raise ValidationError(f"Status inválido. Valores: {', '.join(TaskStatus.values())}")
            parsed_status = TaskStatus(status)

        tasks = self._tasks.find_by_project(project_id, status=parsed_status)
        integration = self._boards.get_integration(project_id)
        meta = {
            "provider": self._boards.active_provider.value,
            "external_enabled": self._boards.is_external_enabled(),
            "board_url": integration.board_url if integration else None,
        }

        if grouped and not status:
            return {
                "board": group_tasks_by_status(tasks),
                "total": len(tasks),
                "kanban": meta,
            }
        return {
            "items": [to_task_output(t) for t in tasks],
            "total": len(tasks),
            "kanban": meta,
        }


class GetTaskUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        collaboration_policy: CollaborationAccessPolicy,
        task_repository: IKanbanTaskRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = collaboration_policy
        self._tasks = task_repository

    def execute(self, *, actor_id: UUID, project_id: UUID, task_id: UUID) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_collaborate(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para visualizar tarefas")

        task = self._tasks.find_by_id(task_id)
        if task is None or task.project_id != project_id:
            raise EntityNotFoundError("Tarefa", str(task_id))
        return to_task_output(task)


class UpdateTaskUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        collaboration_policy: CollaborationAccessPolicy,
        task_repository: IKanbanTaskRepository,
        kanban_task_service: KanbanTaskService,
    ) -> None:
        self._ctx = context_resolver
        self._policy = collaboration_policy
        self._tasks = task_repository
        self._kanban = kanban_task_service

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        task_id: UUID,
        title: str | None = None,
        description: str | None = None,
        assignee_id: UUID | None = ...,
        due_date: date | None = ...,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_collaborate(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para editar tarefas")

        task = self._tasks.find_by_id(task_id)
        if task is None or task.project_id != project_id:
            raise EntityNotFoundError("Tarefa", str(task_id))

        if title is not None:
            title = title.strip()
            if not title:
                raise ValidationError("Título da tarefa é obrigatório")

        if assignee_id is not ...:
            self._policy.validate_assignee(ctx.project, assignee_id)

        updated = self._kanban.update(
            ctx.project,
            task,
            title=title,
            description=description.strip() if description is not None else None,
            assignee_id=assignee_id,
            due_date=due_date,
        )
        return to_task_output(updated)


class MoveTaskUseCase:
    """UC25 — Mover tarefa (sincroniza coluna no Trello)."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        collaboration_policy: CollaborationAccessPolicy,
        task_repository: IKanbanTaskRepository,
        kanban_task_service: KanbanTaskService,
        dependency_validator: TaskDependencyValidator,
    ) -> None:
        self._ctx = context_resolver
        self._policy = collaboration_policy
        self._tasks = task_repository
        self._kanban = kanban_task_service
        self._dep_validator = dependency_validator

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        task_id: UUID,
        status: str,
        position: int | None = None,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_collaborate(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para mover tarefas")

        if not TaskStatus.is_valid(status):
            raise ValidationError(f"Status inválido. Valores: {', '.join(TaskStatus.values())}")

        task = self._tasks.find_by_id(task_id)
        if task is None or task.project_id != project_id:
            raise EntityNotFoundError("Tarefa", str(task_id))

        new_status = TaskStatus(status)
        if new_status == TaskStatus.DONE:
            self._dep_validator.validate_move_to_done(task_id)

        if position is None:
            position = self._tasks.max_position(project_id, new_status) + 1

        updated = self._kanban.update(
            ctx.project,
            task,
            status=new_status,
            position=position,
        )
        return to_task_output(updated)


class DeleteTaskUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        collaboration_policy: CollaborationAccessPolicy,
        task_repository: IKanbanTaskRepository,
        kanban_task_service: KanbanTaskService,
    ) -> None:
        self._ctx = context_resolver
        self._policy = collaboration_policy
        self._tasks = task_repository
        self._kanban = kanban_task_service

    def execute(self, *, actor_id: UUID, project_id: UUID, task_id: UUID) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        task = self._tasks.find_by_id(task_id)
        if task is None or task.project_id != project_id:
            raise EntityNotFoundError("Tarefa", str(task_id))

        if not self._policy.can_delete_task(
            ctx.actor, ctx.project, created_by=task.created_by
        ):
            raise AuthorizationError("Não tem permissão para eliminar esta tarefa")

        self._kanban.delete(ctx.project, task)
        return {"message": "Tarefa eliminada", "id": str(task_id)}
