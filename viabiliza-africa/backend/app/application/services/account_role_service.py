from uuid import UUID

from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.domain.repositories.admin_config_repository import ISubscriptionRepository
from app.domain.repositories.user_repository import IUserRepository


class AccountRoleService:
    """
    Garante que utilizadores com assinatura própria (signup self-service)
    tenham perfil de analista (financial) para criar projectos.
    Colaboradores convidados mantêm role=user e não têm assinatura activa.
    """

    def __init__(
        self,
        user_repository: IUserRepository,
        subscription_repository: ISubscriptionRepository,
    ) -> None:
        self._users = user_repository
        self._subs = subscription_repository

    def ensure_analyst_for_subscriber(self, user: User) -> User:
        if user.role in (UserRole.ADMIN, UserRole.FINANCIAL, UserRole.BANK):
            return user
        if user.role != UserRole.USER:
            return user
        if self._subs.find_active_subscription(user.id) is None:
            return user
        return self._users.update(user.id, role=UserRole.FINANCIAL)

    def ensure_analyst_for_subscriber_by_id(self, user_id: UUID) -> User | None:
        user = self._users.find_by_id(user_id)
        if user is None:
            return None
        return self.ensure_analyst_for_subscriber(user)
