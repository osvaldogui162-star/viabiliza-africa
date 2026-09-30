from uuid import UUID

from app.application.services.project_access_policy import ProjectAccessPolicy
from app.domain.enums.access_action import AccessAction
from app.domain.exceptions.domain_exceptions import (
    AuthorizationError,
    EntityNotFoundError,
    ValidationError,
)
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.user_repository import IUserRepository


class DeleteProjectUseCase:
    """UC09 — Excluir projeto (soft delete)."""

    def __init__(
        self,
        user_repository: IUserRepository,
        project_repository: IProjectRepository,
        access_log_repository: IAccessLogRepository,
        access_policy: ProjectAccessPolicy,
    ) -> None:
        self._users = user_repository
        self._projects = project_repository
        self._access_logs = access_log_repository
        self._policy = access_policy

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))

        project = self._projects.find_by_id(project_id)
        if project is None:
            raise EntityNotFoundError("Projeto", str(project_id))

        if project.has_approved_budget:
            raise ValidationError(
                "Não é possível excluir projeto com orçamento aprovado"
            )

        if not self._policy.can_delete(actor, project):
            raise AuthorizationError("Não tem permissão para excluir este projeto")

        self._projects.soft_delete(project_id)

        self._access_logs.create(
            user_id=actor.id,
            action=AccessAction.PROJECT_DELETED,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"project_id": str(project_id)},
        )

        return {"message": "Projeto excluído com sucesso"}
