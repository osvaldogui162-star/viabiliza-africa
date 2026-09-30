from uuid import UUID

from app.application.services.ingestion_access_policy import IngestionAccessPolicy
from app.application.services.project_access_policy import ProjectAccessPolicy
from app.domain.entities.project import Project
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import (
    AuthorizationError,
    EntityNotFoundError,
)
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.user_repository import IUserRepository


class ProjectContext:
    def __init__(self, actor: User, project: Project, is_shared: bool) -> None:
        self.actor = actor
        self.project = project
        self.is_shared = is_shared


class ProjectContextResolver:
    """Resolve actor + project + permissões (DRY para use cases)."""

    def __init__(
        self,
        user_repository: IUserRepository,
        project_repository: IProjectRepository,
        project_policy: ProjectAccessPolicy,
        ingestion_policy: IngestionAccessPolicy,
    ) -> None:
        self._users = user_repository
        self._projects = project_repository
        self._project_policy = project_policy
        self._ingestion_policy = ingestion_policy

    def resolve(self, actor_id: UUID, project_id: UUID) -> ProjectContext:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        project = self._projects.find_by_id(project_id)
        if project is None:
            raise EntityNotFoundError("Projeto", str(project_id))
        is_shared = self._projects.is_shared_with_user(project_id, actor_id)
        if not self._project_policy.can_view(actor, project, is_shared=is_shared):
            raise AuthorizationError("Não tem acesso a este projeto")
        return ProjectContext(actor, project, is_shared)

    def require_ingest(self, ctx: ProjectContext) -> None:
        if not self._ingestion_policy.can_ingest(ctx.actor, ctx.project):
            raise AuthorizationError("Não tem permissão para ingerir dados neste projeto")

    def require_audit_view(self, ctx: ProjectContext) -> None:
        if not self._ingestion_policy.can_view_audit_trail(
            ctx.actor, ctx.project, is_shared=ctx.is_shared
        ):
            raise AuthorizationError("Não tem permissão para consultar o audit trail")
