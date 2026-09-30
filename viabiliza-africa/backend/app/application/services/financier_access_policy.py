from uuid import UUID

from app.domain.entities.project import Project
from app.domain.entities.project_financing import ProjectFinancing
from app.domain.entities.user import User
from app.domain.enums.project_capability import ProjectCapability
from app.domain.enums.user_role import UserRole


def financing_is_operational(financing: ProjectFinancing) -> bool:
    return financing.is_portfolio_active()


class FinancierAccessPolicy:
    def __init__(self, capability_policy=None) -> None:
        self._capabilities = capability_policy

    def can_register_financing(self, actor: User, project: Project) -> bool:
        if not actor.is_active:
            return False
        if actor.role == UserRole.ADMIN:
            return True
        return actor.role == UserRole.FINANCIAL and project.owner_id == actor.id

    def can_view_financing(
        self,
        actor: User,
        financing: ProjectFinancing,
        *,
        project: Project,
    ) -> bool:
        if not actor.is_active or not financing.is_active:
            return False
        if actor.role == UserRole.ADMIN:
            return True
        if actor.role == UserRole.BANK:
            return (
                actor.bank_code is not None
                and actor.bank_code.lower() == financing.bank_code.lower()
            )
        if actor.role == UserRole.FINANCIAL and project.owner_id == actor.id:
            return True
        if self._capabilities and actor.role == UserRole.USER:
            return self._capabilities.can(
                actor, project, ProjectCapability.VIEW_FINANCING.value
            )
        return False

    def portfolio_bank_code(self, actor: User) -> str | None:
        if actor.role == UserRole.BANK:
            return actor.bank_code.lower() if actor.bank_code else None
        return None

    def can_list_portfolio(self, actor: User) -> bool:
        if not actor.is_active:
            return False
        if actor.role in (UserRole.ADMIN, UserRole.BANK):
            return True
        return actor.role == UserRole.FINANCIAL

    def financial_owner_id_filter(self, actor: User) -> UUID | None:
        if actor.role == UserRole.FINANCIAL:
            return actor.id
        return None

    def can_decide_financing(self, actor: User, financing: ProjectFinancing) -> bool:
        if not actor.is_active or not financing.is_pending_bank():
            return False
        if actor.role == UserRole.ADMIN:
            return True
        if actor.role == UserRole.BANK:
            return (
                actor.bank_code is not None
                and actor.bank_code.lower() == financing.bank_code.lower()
            )
        return False

    def can_operate_financing(
        self,
        actor: User,
        financing: ProjectFinancing,
        *,
        project: Project,
    ) -> bool:
        if not financing_is_operational(financing):
            return False
        return self.can_view_financing(actor, financing, project=project)
