from uuid import UUID

from app.application.dto.project_dto import ProjectDetailOutput
from app.application.services.project_access_policy import ProjectAccessPolicy
from app.application.use_cases.projects.project_mapper import to_project_output
from app.domain.exceptions.domain_exceptions import AuthorizationError, EntityNotFoundError
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.project_share_repository import IProjectShareRepository
from app.domain.repositories.user_repository import IUserRepository


class GetProjectUseCase:
    """UC10 — Visualizar detalhes do projeto (com saldo automático)."""

    def __init__(
        self,
        user_repository: IUserRepository,
        project_repository: IProjectRepository,
        project_share_repository: IProjectShareRepository,
        access_policy: ProjectAccessPolicy,
        cost_item_repository: ICostItemRepository,
    ) -> None:
        self._users = user_repository
        self._projects = project_repository
        self._shares = project_share_repository
        self._policy = access_policy
        self._items = cost_item_repository

    def execute(self, *, actor_id: UUID, project_id: UUID) -> ProjectDetailOutput:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))

        project = self._projects.find_by_id(project_id)
        if project is None:
            raise EntityNotFoundError("Projeto", str(project_id))

        is_shared = self._projects.is_shared_with_user(project_id, actor_id)
        if not self._policy.can_view(actor, project, is_shared=is_shared):
            raise AuthorizationError("Não tem acesso a este projeto")

        owner = self._users.find_by_id(project.owner_id)
        shares_count = self._shares.count_by_project(project_id)
        spend_summary = self._items.summarize_spend_by_project(project_id)

        my_access = None
        if is_shared and project.owner_id != actor_id:
            actor_share = self._shares.find_by_project_and_user(project_id, actor_id)
            if actor_share:
                my_access = {
                    "permission": actor_share.permission.value,
                    "job_title": actor_share.job_title,
                    "effective_capabilities": actor_share.effective_capabilities(),
                }

        project_output = to_project_output(
            project,
            owner=owner,
            actor_id=actor_id,
            is_shared=is_shared and project.owner_id != actor_id,
            shares_count=shares_count,
            spend_summary=spend_summary,
            my_access=my_access,
        )

        return ProjectDetailOutput(project=project_output, shares=[])
