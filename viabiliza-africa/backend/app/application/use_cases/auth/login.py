from datetime import datetime, timedelta, timezone

from app.application.dto.auth_dto import AuthOutput, LoginInput
from app.application.mappers.user_output_mapper import user_to_output
from app.application.interfaces.password_hasher import IPasswordHasher
from app.application.interfaces.token_service import ITokenService, TokenPayload
from app.application.services.account_role_service import AccountRoleService
from app.application.services.user_access_enforcement import UserAccessEnforcementService
from app.config import Config
from app.domain.enums.access_action import AccessAction
from app.domain.exceptions.domain_exceptions import AuthenticationError
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.user_repository import IUserRepository
from app.infrastructure.auth.auth_rate_limiter import AuthRateLimiter


class LoginUseCase:
    """UC02 — Fazer login."""

    def __init__(
        self,
        user_repository: IUserRepository,
        access_log_repository: IAccessLogRepository,
        password_hasher: IPasswordHasher,
        token_service: ITokenService,
        account_role_service: AccountRoleService,
        access_enforcement: UserAccessEnforcementService,
        rate_limiter: AuthRateLimiter,
        config: Config,
    ) -> None:
        self._users = user_repository
        self._access_logs = access_log_repository
        self._hasher = password_hasher
        self._tokens = token_service
        self._account_roles = account_role_service
        self._access = access_enforcement
        self._rate_limiter = rate_limiter
        self._config = config

    def execute(self, input_data: LoginInput) -> AuthOutput:
        email = input_data.email.strip().lower()
        self._rate_limiter.check("login", email)
        if input_data.ip_address:
            self._rate_limiter.check("login_ip", input_data.ip_address)

        user = self._users.find_by_email(email)

        if user is None:
            self._log_failed(email, input_data)
            raise AuthenticationError()

        if not user.is_active:
            self._log_failed(email, input_data, user_id=user.id)
            raise AuthenticationError(
                "Conta aguarda aprovação ou foi desactivada. Contacte o suporte."
            )

        if not user.password_hash:
            self._log_failed(email, input_data, user_id=user.id)
            raise AuthenticationError(
                "Esta conta utiliza Google. Use «Continuar com Google» para entrar."
            )

        if not self._hasher.verify(input_data.password, user.password_hash):
            self._log_failed(email, input_data, user_id=user.id)
            raise AuthenticationError()

        user = self._access.enforce(user)
        user = self._account_roles.ensure_analyst_for_subscriber(user)

        payload = TokenPayload(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
        )
        access_token = self._tokens.create_access_token(payload)
        refresh_token = self._tokens.create_refresh_token()

        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(days=self._config.JWT_REFRESH_TOKEN_EXPIRES_DAYS)
        ).isoformat()
        self._users.save_refresh_token(
            user.id,
            self._tokens.hash_token(refresh_token),
            expires_at,
        )

        self._access_logs.create(
            user_id=user.id,
            action=AccessAction.LOGIN_SUCCESS,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
            metadata={"email": email},
        )

        return AuthOutput(
            user=user_to_output(user),
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=self._tokens.get_access_token_expires_seconds(),
        )

    def _log_failed(self, email: str, input_data: LoginInput, user_id=None) -> None:
        self._access_logs.create(
            user_id=user_id,
            action=AccessAction.LOGIN_FAILED,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
            metadata={"email": email},
        )
