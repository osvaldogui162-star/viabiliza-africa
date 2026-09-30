from uuid import UUID

from app.application.services.collaboration_access_policy import CollaborationAccessPolicy
from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.services.task_dependency_validator import TaskDependencyValidator
from app.application.use_cases.collaboration.mappers import to_dependency_output
from app.domain.exceptions.domain_exceptions import AuthorizationError, EntityNotFoundError
from app.domain.repositories.collaboration_repository import (
    ITaskDependencyRepository,
)


class CreateTaskDependencyUseCase:
    """UC26 — Criar dependência entre tarefas."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        collaboration_policy: CollaborationAccessPolicy,
        dependency_repository: ITaskDependencyRepository,
        dependency_validator: TaskDependencyValidator,
    ) -> None:
        self._ctx = context_resolver
        self._policy = collaboration_policy
        self._deps = dependency_repository
        self._validator = dependency_validator

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        predecessor_task_id: UUID,
        successor_task_id: UUID,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_manage_dependencies(ctx.actor, ctx.project):
            raise AuthorizationError("Não tem permissão para gerir dependências entre tarefas")

        self._validator.validate_create(project_id, predecessor_task_id, successor_task_id)

        dep = self._deps.create(
            project_id=project_id,
            predecessor_task_id=predecessor_task_id,
            successor_task_id=successor_task_id,
            created_by=actor_id,
        )
        return to_dependency_output(dep)


class ListTaskDependenciesUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        collaboration_policy: CollaborationAccessPolicy,
        dependency_repository: ITaskDependencyRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = collaboration_policy
        self._deps = dependency_repository

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_collaborate(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para visualizar dependências")

        items = self._deps.find_by_project(project_id)
        return {
            "items": [to_dependency_output(d) for d in items],
            "total": len(items),
        }


class DeleteTaskDependencyUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        collaboration_policy: CollaborationAccessPolicy,
        dependency_repository: ITaskDependencyRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = collaboration_policy
        self._deps = dependency_repository

    def execute(self, *, actor_id: UUID, project_id: UUID, dependency_id: UUID) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_manage_dependencies(ctx.actor, ctx.project):
            raise AuthorizationError("Não tem permissão para eliminar dependências")

        dep = self._deps.find_by_id(dependency_id)
        if dep is None or dep.project_id != project_id:
            raise EntityNotFoundError("Dependência", str(dependency_id))

        self._deps.delete(dependency_id)
        return {"message": "Dependência eliminada", "id": str(dependency_id)}
