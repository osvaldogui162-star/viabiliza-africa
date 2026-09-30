from uuid import UUID

from app.application.services.project_access_policy import ProjectAccessPolicy
from app.application.services.shared_project_capability_policy import SharedProjectCapabilityPolicy
from app.domain.entities.project import Project
from app.domain.entities.user import User
from app.domain.enums.project_capability import ProjectCapability
from app.domain.enums.user_role import UserRole
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.user_repository import IUserRepository


class CollaborationAccessPolicy:
    """Política de acesso para tarefas e chat (Módulo 5)."""

    def __init__(
        self,
        project_policy: ProjectAccessPolicy,
        project_repository: IProjectRepository,
        user_repository: IUserRepository,
        capability_policy: SharedProjectCapabilityPolicy | None = None,
    ) -> None:
        self._project_policy = project_policy
        self._projects = project_repository
        self._users = user_repository
        self._capabilities = capability_policy

    def can_collaborate(
        self, user: User, project: Project, *, is_shared: bool
    ) -> bool:
        """UC24, UC25, UC27 — criar/mover tarefas e chat."""
        if self._capabilities and not self._capabilities.is_owner_or_admin(user, project):
            return self._capabilities.can(
                user, project, ProjectCapability.MANAGE_COLLABORATION.value
            )
        return self._project_policy.can_view(user, project, is_shared=is_shared)

    def can_manage_dependencies(self, user: User, project: Project) -> bool:
        """UC26 — dependências: admin e analista (dono)."""
        if not user.is_active or project.is_deleted:
            return False
        if user.role == UserRole.ADMIN:
            return True
        return user.role == UserRole.FINANCIAL and project.owner_id == user.id

    def can_delete_task(self, user: User, project: Project, *, created_by: UUID) -> bool:
        if not user.is_active or project.is_deleted:
            return False
        if user.role == UserRole.ADMIN:
            return True
        if user.role == UserRole.FINANCIAL and project.owner_id == user.id:
            return True
        return user.id == created_by

    def validate_assignee(self, project: Project, assignee_id: UUID | None) -> None:
        """Responsável deve ser membro com acesso ao projeto."""
        if assignee_id is None:
            return

        assignee = self._users.find_by_id(assignee_id)
        if assignee is None or not assignee.is_active:
            from app.domain.exceptions.domain_exceptions import ValidationError

            raise ValidationError("Responsável inválido ou inactivo")

        if assignee.role == UserRole.ADMIN:
            return
        if project.owner_id == assignee_id:
            return
        if self._projects.is_shared_with_user(project.id, assignee_id):
            return

        from app.domain.exceptions.domain_exceptions import ValidationError

        raise ValidationError("O responsável não tem acesso a este projeto")
