from uuid import UUID

from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import AuthorizationError, EntityNotFoundError
from app.domain.repositories.user_repository import IUserRepository


class AdminAccessPolicy:
    """Política de acesso para Módulo 7 — apenas Administrador."""

    def __init__(self, user_repository: IUserRepository) -> None:
        self._users = user_repository

    def require_admin(self, actor_id: UUID) -> User:
        user = self._users.find_by_id(actor_id)
        if user is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        if not user.can_manage_system_settings():
            raise AuthorizationError("Apenas administradores podem aceder a esta configuração")
        return user
