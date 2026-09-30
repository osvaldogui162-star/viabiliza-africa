from uuid import UUID

from app.application.dto.auth_dto import UpdateUserPreferencesInput, UserOutput
from app.application.mappers.user_output_mapper import user_to_output
from app.application.services.fx_service import normalize_currency
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from app.domain.repositories.user_repository import IUserRepository


class UpdateUserPreferencesUseCase:
    """Actualizar preferências do utilizador autenticado (moeda de exibição)."""

    def __init__(self, user_repository: IUserRepository) -> None:
        self._users = user_repository

    def execute(self, data: UpdateUserPreferencesInput) -> UserOutput:
        user = self._users.find_by_id(data.user_id)
        if user is None or not user.is_active:
            raise EntityNotFoundError("Utilizador", str(data.user_id))

        currency = normalize_currency(data.preferred_currency)
        updated = self._users.update(user.id, preferred_currency=currency)
        return user_to_output(updated)
