from datetime import datetime, timedelta, timezone

from app.application.dto.auth_dto import AuthOutput, RefreshTokenInput
from app.application.mappers.user_output_mapper import user_to_output
from app.application.interfaces.token_service import ITokenService, TokenPayload
from app.application.services.account_role_service import AccountRoleService
from app.application.services.user_access_enforcement import UserAccessEnforcementService
from app.config import Config
from app.domain.enums.access_action import AccessAction
from app.domain.exceptions.domain_exceptions import AuthenticationError
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.user_repository import IUserRepository


class RefreshTokenUseCase:
    """Renovar access token via refresh token."""

    def __init__(
        self,
        user_repository: IUserRepository,
        access_log_repository: IAccessLogRepository,
        token_service: ITokenService,
        account_role_service: AccountRoleService,
        access_enforcement: UserAccessEnforcementService,
        config: Config,
    ) -> None:
        self._users = user_repository
        self._access_logs = access_log_repository
        self._tokens = token_service
        self._account_roles = account_role_service
        self._access = access_enforcement
        self._config = config

    def execute(self, input_data: RefreshTokenInput) -> AuthOutput:
        token_hash = self._tokens.hash_token(input_data.refresh_token)
        user = self._users.find_by_refresh_token(token_hash)

        if user is None or not user.is_active:
            raise AuthenticationError("Refresh token inválido ou expirado")

        user = self._access.enforce(user)
        user = self._account_roles.ensure_analyst_for_subscriber(user)

        self._users.revoke_refresh_token(token_hash)

        payload = TokenPayload(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
        )
        access_token = self._tokens.create_access_token(payload)
        new_refresh = self._tokens.create_refresh_token()

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(days=self._config.JWT_REFRESH_TOKEN_EXPIRES_DAYS)
        ).isoformat()
        self._users.save_refresh_token(
            user.id,
            self._tokens.hash_token(new_refresh),
            expires_at,
        )

        self._access_logs.create(
            user_id=user.id,
            action=AccessAction.TOKEN_REFRESHED,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
        )

        return AuthOutput(
            user=user_to_output(user),
            access_token=access_token,
            refresh_token=new_refresh,
            token_type="Bearer",
            expires_in=self._tokens.get_access_token_expires_seconds(),
        )
