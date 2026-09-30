from uuid import UUID

from app.application.dto.auth_dto import UserOutput
from app.application.mappers.user_output_mapper import user_to_output
from app.application.services.account_role_service import AccountRoleService
from app.application.services.user_access_enforcement import UserAccessEnforcementService
from app.domain.exceptions.domain_exceptions import AuthenticationError, EntityNotFoundError
from app.domain.repositories.user_repository import IUserRepository


class GetCurrentUserUseCase:
    """Obter perfil do utilizador autenticado."""

    def __init__(
        self,
        user_repository: IUserRepository,
        account_role_service: AccountRoleService,
        access_enforcement: UserAccessEnforcementService,
    ) -> None:
        self._users = user_repository
        self._account_roles = account_role_service
        self._access = access_enforcement

    def execute(self, user_id: UUID) -> UserOutput:
        user = self._users.find_by_id(user_id)
        if user is None:
            raise EntityNotFoundError("Utilizador", str(user_id))

        try:
            user = self._access.enforce(user)
        except AuthenticationError:
            raise EntityNotFoundError("Utilizador", str(user_id)) from None

        user = self._account_roles.ensure_analyst_for_subscriber(user)

        return user_to_output(user)
