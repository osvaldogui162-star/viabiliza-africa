from app.application.dto.auth_dto import ResetPasswordInput
from app.application.interfaces.password_hasher import IPasswordHasher
from app.application.interfaces.token_service import ITokenService
from app.domain.enums.access_action import AccessAction
from app.domain.exceptions.domain_exceptions import AuthenticationError, ValidationError
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.user_repository import IUserRepository

_PASSWORD_MIN_LENGTH = 8


class ResetPasswordUseCase:
    """UC03 — Concluir redefinição de palavra-passe com token."""

    def __init__(
        self,
        user_repository: IUserRepository,
        access_log_repository: IAccessLogRepository,
        password_hasher: IPasswordHasher,
        token_service: ITokenService,
    ) -> None:
        self._users = user_repository
        self._access_logs = access_log_repository
        self._hasher = password_hasher
        self._tokens = token_service

    def execute(self, input_data: ResetPasswordInput) -> dict:
        if len(input_data.new_password) < _PASSWORD_MIN_LENGTH:
            raise ValidationError(
                f"Palavra-passe deve ter pelo menos {_PASSWORD_MIN_LENGTH} caracteres"
            )

        token_hash = self._tokens.hash_token(input_data.token)
        user = self._users.find_by_password_reset_token(token_hash)

        if user is None or not user.is_active:
            raise AuthenticationError("Token de recuperação inválido ou expirado")

        password_hash = self._hasher.hash(input_data.new_password)
        self._users.update(user.id, password_hash=password_hash)
        self._users.clear_password_reset_token(user.id)
        self._users.revoke_all_refresh_tokens(user.id)

        self._access_logs.create(
            user_id=user.id,
            action=AccessAction.PASSWORD_RESET_COMPLETED,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
        )

        return {"message": "Palavra-passe redefinida com sucesso"}
