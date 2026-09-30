from uuid import UUID

from app.application.interfaces.token_service import ITokenService
from app.domain.enums.access_action import AccessAction
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.user_repository import IUserRepository


class LogoutUseCase:
    """Revogar refresh token e registar logout."""

    def __init__(
        self,
        user_repository: IUserRepository,
        access_log_repository: IAccessLogRepository,
        token_service: ITokenService,
    ) -> None:
        self._users = user_repository
        self._access_logs = access_log_repository
        self._tokens = token_service

    def execute(
        self,
        *,
        user_id: UUID,
        refresh_token: str | None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict:
        if refresh_token:
            self._users.revoke_refresh_token(self._tokens.hash_token(refresh_token))
        else:
            self._users.revoke_all_refresh_tokens(user_id)

        self._access_logs.create(
            user_id=user_id,
            action=AccessAction.LOGOUT,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return {"message": "Logout efetuado com sucesso"}
