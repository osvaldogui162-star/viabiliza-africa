from uuid import UUID

from app.domain.entities.project import Project
from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole


class ProjectAccessPolicy:
    """
    Política centralizada de acesso a projetos (Single Responsibility).
    Consolida regras RBAC e de negócio do Módulo 2.
    """

    def can_create(self, user: User) -> bool:
        return user.is_active and user.role in (UserRole.ADMIN, UserRole.FINANCIAL)

    def can_list_all(self, user: User) -> bool:
        return user.is_active and user.role == UserRole.ADMIN

    def can_view(
        self,
        user: User,
        project: Project,
        *,
        is_shared: bool,
    ) -> bool:
        if not user.is_active or project.is_deleted:
            return False
        if user.role == UserRole.ADMIN:
            return True
        if project.owner_id == user.id:
            return True
        return is_shared

    def can_edit(self, user: User, project: Project, *, shared_may_edit: bool = False) -> bool:
        if not user.is_active or project.is_deleted or not project.is_editable:
            return False
        if user.role == UserRole.ADMIN:
            return True
        if user.role == UserRole.FINANCIAL and project.owner_id == user.id:
            return True
        return shared_may_edit

    def can_delete(self, user: User, project: Project) -> bool:
        if not user.is_active or project.is_deleted or not project.can_be_deleted():
            return False
        if user.role == UserRole.ADMIN:
            return True
        if (
            user.role == UserRole.FINANCIAL
            and project.owner_id == user.id
            and project.status.is_editable()
        ):
            return True
        return False

    def can_share(self, user: User, project: Project) -> bool:
        if not user.is_active or project.is_deleted:
            return False
        if user.role == UserRole.ADMIN:
            return True
        if user.role == UserRole.FINANCIAL and project.owner_id == user.id:
            return True
        return False

    def resolve_list_scope(self, user: User) -> str:
        """Retorna o âmbito de listagem: all, owned_and_shared, shared."""
        if user.role == UserRole.ADMIN:
            return "all"
        if user.role == UserRole.FINANCIAL:
            return "owned_and_shared"
        return "shared"

    def is_owner(self, user_id: UUID, project: Project) -> bool:
        return project.owner_id == user_id
