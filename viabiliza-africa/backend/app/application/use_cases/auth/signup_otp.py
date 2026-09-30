import re
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.application.dto.auth_dto import (
    AuthOutput,
    SignupOtpRequestInput,
    SignupOtpResendInput,
    SignupOtpVerifyInput,
)
from app.application.mappers.user_output_mapper import user_to_output
from app.application.interfaces.email_service import IEmailService
from app.application.interfaces.password_hasher import IPasswordHasher
from app.application.interfaces.token_service import ITokenService, TokenPayload
from app.application.services.notification_service import NotificationService
from app.application.services.registration_invite_fulfillment import (
    RegistrationInviteFulfillmentService,
)
from app.application.services.registration_policy_service import RegistrationPolicyService
from app.application.use_cases.subscriptions.public_plans import SubscribeToPlanUseCase
from app.config import Config
from app.domain.enums.access_action import AccessAction
from app.domain.exceptions.domain_exceptions import (
    AccountPendingApprovalError,
    AuthenticationError,
    ConflictError,
    ValidationError,
)
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.admin_config_repository import ISubscriptionRepository
from app.domain.repositories.user_repository import IUserRepository
from app.infrastructure.auth.auth_rate_limiter import AuthRateLimiter

_PASSWORD_MIN_LENGTH = 8
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _validate_signup_fields(email: str, password: str, full_name: str) -> None:
    if not _EMAIL_PATTERN.match(email):
        raise ValidationError("Email inválido")
    if len(password) < _PASSWORD_MIN_LENGTH:
        raise ValidationError(
            f"Palavra-passe deve ter pelo menos {_PASSWORD_MIN_LENGTH} caracteres"
        )
    if not full_name.strip():
        raise ValidationError("Nome completo é obrigatório")


def _generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


class RequestSignupOtpUseCase:
    """Inicia registo público — envia OTP por email."""

    def __init__(
        self,
        user_repository: IUserRepository,
        access_log_repository: IAccessLogRepository,
        password_hasher: IPasswordHasher,
        token_service: ITokenService,
        email_service: IEmailService,
        registration_policy: RegistrationPolicyService,
        rate_limiter: AuthRateLimiter,
        config: Config,
    ) -> None:
        self._users = user_repository
        self._access_logs = access_log_repository
        self._hasher = password_hasher
        self._tokens = token_service
        self._email = email_service
        self._registration = registration_policy
        self._rate_limiter = rate_limiter
        self._config = config

    def execute(self, input_data: SignupOtpRequestInput) -> dict:
        email = input_data.email.strip().lower()
        _validate_signup_fields(email, input_data.password, input_data.full_name)
        self._registration.validate_terms(
            terms_accepted=input_data.terms_accepted,
            terms_version=input_data.terms_version,
        )
        self._registration.decide_new_user(email)
        self._rate_limiter.check("signup_otp", email)
        if input_data.ip_address:
            self._rate_limiter.check("signup_otp_ip", input_data.ip_address)

        existing = self._users.find_by_email(email)
        if existing:
            if existing.auth_provider == "google" and not existing.password_hash:
                raise ConflictError(
                    "Este email já está registado com Google. Use «Continuar com Google»."
                )
            raise ConflictError(
                "Este email já está registado. Inicie sessão ou recupere a palavra-passe."
            )

        last_created = self._users.latest_signup_otp_created_at(email)
        if last_created:
            created = datetime.fromisoformat(last_created.replace("Z", "+00:00"))
            cooldown = timedelta(seconds=self._config.SIGNUP_OTP_RESEND_COOLDOWN_SECONDS)
            if datetime.now(timezone.utc) - created < cooldown:
                raise ValidationError(
                    f"Aguarde {self._config.SIGNUP_OTP_RESEND_COOLDOWN_SECONDS} segundos antes de pedir um novo código"
                )

        otp = _generate_otp()
        code_hash = self._tokens.hash_token(otp)
        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(minutes=self._config.SIGNUP_OTP_EXPIRES_MINUTES)
        ).isoformat()

        password_hash = self._hasher.hash(input_data.password)
        self._users.save_signup_otp(
            email=email,
            code_hash=code_hash,
            full_name=input_data.full_name.strip(),
            password_hash=password_hash,
            expires_at=expires_at,
        )

        sent = self._email.send_signup_otp(
            email,
            input_data.full_name.strip(),
            otp,
            self._config.SIGNUP_OTP_EXPIRES_MINUTES,
        )

        self._access_logs.create(
            user_id=None,
            action=AccessAction.SIGNUP_OTP_REQUESTED,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
            metadata={"email": email},
        )

        response: dict = {
            "message": (
                "Enviámos um código de verificação para o seu email. "
                "Introduza-o para concluir o registo."
            ),
            "expires_in_minutes": self._config.SIGNUP_OTP_EXPIRES_MINUTES,
            "email_sent": sent,
        }
        if self._config.DEBUG and not sent:
            response["dev_otp"] = otp
        return response


class VerifySignupOtpUseCase:
    """Valida OTP, cria conta, atribui plano gratuito e inicia sessão."""

    def __init__(
        self,
        user_repository: IUserRepository,
        access_log_repository: IAccessLogRepository,
        subscription_repository: ISubscriptionRepository,
        token_service: ITokenService,
        registration_policy: RegistrationPolicyService,
        invite_fulfillment: RegistrationInviteFulfillmentService,
        notification_service: NotificationService,
        rate_limiter: AuthRateLimiter,
        config: Config,
    ) -> None:
        self._users = user_repository
        self._access_logs = access_log_repository
        self._subs_repo = subscription_repository
        self._tokens = token_service
        self._registration = registration_policy
        self._fulfillment = invite_fulfillment
        self._notifications = notification_service
        self._rate_limiter = rate_limiter
        self._config = config

    def execute(self, input_data: SignupOtpVerifyInput) -> AuthOutput:
        email = input_data.email.strip().lower()
        code = input_data.code.strip()
        self._registration.validate_terms(
            terms_accepted=input_data.terms_accepted,
            terms_version=input_data.terms_version,
        )
        self._rate_limiter.check("signup_verify", email)

        if not code or len(code) != 6 or not code.isdigit():
            raise ValidationError("Código inválido — introduza os 6 dígitos")

        if self._users.find_by_email(email):
            raise ConflictError("Este email já está registado")

        pending = self._users.find_pending_signup_otp(email)
        if pending is None:
            raise ValidationError(
                "Código expirado ou inexistente. Solicite um novo código de verificação."
            )

        code_hash = self._tokens.hash_token(code)
        if code_hash != pending["code_hash"]:
            attempts = self._users.increment_signup_otp_attempts(UUID(pending["id"]))
            if attempts >= self._config.SIGNUP_OTP_MAX_ATTEMPTS:
                self._users.consume_signup_otp(UUID(pending["id"]))
                raise ValidationError(
                    "Demasiadas tentativas incorrectas. Solicite um novo código."
                )
            raise AuthenticationError("Código incorrecto")

        decision = self._registration.decide_new_user(email)
        now = datetime.now(timezone.utc).isoformat()

        user = self._users.create(
            email=email,
            full_name=pending["full_name"],
            password_hash=pending["password_hash"],
            role=decision.role,
            email_verified=True,
            is_active=decision.is_active,
            terms_accepted_at=now,
            terms_version=self._registration.terms_version,
        )
        self._users.consume_signup_otp(UUID(pending["id"]))

        if decision.invites:
            self._fulfillment.fulfill(user.id, decision.invites)

        if decision.assign_free_plan:
            subscribe = SubscribeToPlanUseCase(self._subs_repo)
            subscribe.execute(
                user_id=user.id,
                plan_code="free",
                billing_cycle="monthly",
                currency="AOA",
            )

        self._notifications.notify_admins_new_registration(
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            provider="email",
            pending_approval=not decision.is_active,
        )

        if not decision.is_active:
            raise AccountPendingApprovalError(user.email)

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
            action=AccessAction.SIGNUP_COMPLETED,
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


class ResendSignupOtpUseCase:
    """Reenvia OTP se existir pedido pendente (não revela se email já registado)."""

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

    def execute(self, input_data: SignupOtpResendInput) -> dict:
        email = input_data.email.strip().lower()

        if self._users.find_by_email(email):
            return {
                "message": (
                    "Se existir um registo pendente para este email, "
                    "receberá um novo código em breve."
                )
            }

        pending = self._users.find_pending_signup_otp(email)
        if pending is None:
            return {
                "message": (
                    "Se existir um registo pendente para este email, "
                    "receberá um novo código em breve."
                )
            }

        last_created = self._users.latest_signup_otp_created_at(email)
        if last_created:
            created = datetime.fromisoformat(last_created.replace("Z", "+00:00"))
            cooldown = timedelta(seconds=self._config.SIGNUP_OTP_RESEND_COOLDOWN_SECONDS)
            if datetime.now(timezone.utc) - created < cooldown:
                raise ValidationError(
                    f"Aguarde {self._config.SIGNUP_OTP_RESEND_COOLDOWN_SECONDS} segundos antes de reenviar"
                )

        otp = _generate_otp()
        code_hash = self._tokens.hash_token(otp)
        expires_at = (
            datetime.now(timezone.utc)
            + timedelta(minutes=self._config.SIGNUP_OTP_EXPIRES_MINUTES)
        ).isoformat()

        self._users.save_signup_otp(
            email=email,
            code_hash=code_hash,
            full_name=pending["full_name"],
            password_hash=pending["password_hash"],
            expires_at=expires_at,
        )

        sent = self._email.send_signup_otp(
            email,
            pending["full_name"],
            otp,
            self._config.SIGNUP_OTP_EXPIRES_MINUTES,
        )

        self._access_logs.create(
            user_id=None,
            action=AccessAction.SIGNUP_OTP_REQUESTED,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
            metadata={"email": email, "resend": True},
        )

        response: dict = {
            "message": (
                "Se existir um registo pendente para este email, "
                "receberá um novo código em breve."
            ),
            "email_sent": sent,
        }
        if self._config.DEBUG and not sent:
            response["dev_otp"] = otp
        return response
