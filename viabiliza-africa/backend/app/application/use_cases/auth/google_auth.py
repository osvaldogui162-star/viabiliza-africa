from datetime import datetime, timedelta, timezone

from app.application.dto.auth_dto import AuthOutput, GoogleAuthInput
from app.application.mappers.user_output_mapper import user_to_output
from app.application.interfaces.token_service import ITokenService, TokenPayload
from app.application.services.account_role_service import AccountRoleService
from app.application.services.notification_service import NotificationService
from app.application.services.registration_invite_fulfillment import (
    RegistrationInviteFulfillmentService,
)
from app.application.services.registration_policy_service import RegistrationPolicyService
from app.application.services.user_access_enforcement import UserAccessEnforcementService
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
from app.infrastructure.auth.google_token_verifier import GoogleTokenVerifier


class GoogleAuthUseCase:
    """Login ou registo via Google OAuth (ID token ou authorization code)."""

    def __init__(
        self,
        user_repository: IUserRepository,
        subscription_repository: ISubscriptionRepository,
        access_log_repository: IAccessLogRepository,
        token_service: ITokenService,
        account_role_service: AccountRoleService,
        google_verifier: GoogleTokenVerifier,
        registration_policy: RegistrationPolicyService,
        invite_fulfillment: RegistrationInviteFulfillmentService,
        notification_service: NotificationService,
        rate_limiter: AuthRateLimiter,
        access_enforcement: UserAccessEnforcementService,
        config: Config,
    ) -> None:
        self._users = user_repository
        self._subs_repo = subscription_repository
        self._access_logs = access_log_repository
        self._tokens = token_service
        self._account_roles = account_role_service
        self._google = google_verifier
        self._registration = registration_policy
        self._fulfillment = invite_fulfillment
        self._notifications = notification_service
        self._rate_limiter = rate_limiter
        self._access = access_enforcement
        self._config = config

    def execute(self, input_data: GoogleAuthInput) -> tuple[AuthOutput, bool]:
        if input_data.credential:
            payload = self._google.verify_id_token(input_data.credential)
        elif input_data.code:
            payload = self._google.exchange_authorization_code(input_data.code)
        else:
            raise ValidationError("Credencial Google em falta")

        profile = self._google.extract_profile(payload)
        self._rate_limiter.check("google_auth", profile["email"])
        if input_data.ip_address:
            self._rate_limiter.check("google_auth_ip", input_data.ip_address)

        is_new_user = False

        user = self._users.find_by_google_id(profile["google_id"])
        if user is None:
            user = self._users.find_by_email(profile["email"])
            if user is not None:
                user = self._link_existing_user(user, profile)
            else:
                user = self._create_google_user(profile, input_data)
                is_new_user = True

        if not user.is_active:
            raise AuthenticationError(
                "Conta aguarda aprovação ou foi desactivada. Contacte o suporte."
            )

        user = self._access.enforce(user)
        user = self._account_roles.ensure_analyst_for_subscriber(user)

        auth_output = self._issue_tokens(user)
        self._access_logs.create(
            user_id=user.id,
            action=AccessAction.GOOGLE_SIGNUP_COMPLETED if is_new_user else AccessAction.GOOGLE_LOGIN_SUCCESS,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
            metadata={"email": profile["email"], "provider": "google"},
        )
        return auth_output, is_new_user

    def _link_existing_user(self, user, profile: dict):
        if user.google_id and user.google_id != profile["google_id"]:
            raise ConflictError(
                "Este email já está associado a outra conta Google"
            )
        if user.google_id:
            return user

        if user.password_hash and not user.google_id:
            raise ConflictError(
                "Este email já está registado com palavra-passe. "
                "Inicie sessão com email e palavra-passe para associar Google nas definições."
            )

        updates: dict = {"google_id": profile["google_id"]}
        if not user.full_name.strip():
            updates["full_name"] = profile["full_name"]
        if not user.email_verified:
            updates["email_verified"] = True
        if not user.password_hash:
            updates["auth_provider"] = "google"

        return self._users.update(user.id, **updates)

    def _create_google_user(self, profile: dict, input_data: GoogleAuthInput):
        self._registration.validate_terms(
            terms_accepted=input_data.terms_accepted,
            terms_version=input_data.terms_version,
        )
        decision = self._registration.decide_new_user(profile["email"])
        now = datetime.now(timezone.utc).isoformat()

        user = self._users.create(
            email=profile["email"],
            full_name=profile["full_name"],
            role=decision.role,
            password_hash=None,
            google_id=profile["google_id"],
            auth_provider="google",
            email_verified=True,
            is_active=decision.is_active,
            terms_accepted_at=now,
            terms_version=self._registration.terms_version,
        )

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
            provider="google",
            pending_approval=not decision.is_active,
        )

        if not decision.is_active:
            raise AccountPendingApprovalError(user.email)

        return user

    def _issue_tokens(self, user) -> AuthOutput:
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
        return AuthOutput(
            user=user_to_output(user),
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=self._tokens.get_access_token_expires_seconds(),
        )
