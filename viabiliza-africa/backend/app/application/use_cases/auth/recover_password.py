import secrets
from datetime import datetime, timedelta, timezone

from app.application.dto.auth_dto import PasswordRecoveryInput
from app.application.interfaces.email_service import IEmailService
from app.application.interfaces.token_service import ITokenService
from app.config import Config
from app.domain.enums.access_action import AccessAction
from app.domain.exceptions.domain_exceptions import ValidationError
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.user_repository import IUserRepository


class RecoverPasswordUseCase:
    """UC03 — Solicitar recuperação de palavra-passe por email."""

    def __init__(
        self,
        user_repository: IUserRepository,
        access_log_repository: IAccessLogRepository,
        token_service: ITokenService,
        email_service: IEmailService,
        config: Config,
    ) -> None:
        self._users = user_repository
        self._access_logs = access_log_repository
        self._tokens = token_service
        self._email = email_service
        self._config = config

    def execute(self, input_data: PasswordRecoveryInput) -> dict:
        email = input_data.email.strip().lower()
        user = self._users.find_by_email(email)

        if user is None:
            raise ValidationError("Não existe nenhuma conta registada com este email.")

        if not user.is_active:
            raise ValidationError(
                "Conta aguarda aprovação ou foi desactivada. Contacte o suporte."
            )

        raw_token = secrets.token_urlsafe(32)
        token_hash = self._tokens.hash_token(raw_token)
        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(hours=self._config.PASSWORD_RESET_TOKEN_EXPIRES_HOURS)
        ).isoformat()

        self._users.save_password_reset_token(user.id, token_hash, expires_at)

        reset_url = f"{self._config.FRONTEND_RESET_PASSWORD_URL}?token={raw_token}"
        self._email.send_password_reset(user.email, reset_url, user.full_name)

        self._access_logs.create(
            user_id=user.id,
            action=AccessAction.PASSWORD_RESET_REQUESTED,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
            metadata={"email": email},
        )

        return {
            "message": (
                "Enviámos um link seguro para o seu email. "
                "Siga as instruções para redefinir a palavra-passe."
            )
        }
