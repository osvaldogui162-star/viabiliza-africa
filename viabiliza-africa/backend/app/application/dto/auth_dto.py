from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class LoginInput:
    email: str
    password: str
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True)
class RegisterUserInput:
    email: str
    password: str
    full_name: str
    role: str
    admin_user_id: UUID
    bank_code: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True)
class PasswordRecoveryInput:
    email: str
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True)
class ResetPasswordInput:
    token: str
    new_password: str
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True)
class RefreshTokenInput:
    refresh_token: str
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True)
class SignupOtpRequestInput:
    email: str
    password: str
    full_name: str
    terms_accepted: bool = False
    terms_version: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True)
class SignupOtpVerifyInput:
    email: str
    code: str
    terms_accepted: bool = False
    terms_version: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True)
class SignupOtpResendInput:
    email: str
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True)
class GoogleAuthInput:
    credential: str | None = None
    code: str | None = None
    terms_accepted: bool = False
    terms_version: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True)
class UpdateUserPreferencesInput:
    user_id: UUID
    preferred_currency: str
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True)
class UserOutput:
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    preferred_currency: str
    bank_code: str | None
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class AuthOutput:
    user: UserOutput
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


@dataclass(frozen=True)
class UpdateUserRoleInput:
    target_user_id: UUID
    role: str
    admin_user_id: UUID
    bank_code: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True)
class UpdateUserInput:
    target_user_id: UUID
    admin_user_id: UUID
    full_name: str | None = None
    role: str | None = None
    bank_code: str | None = None
    is_active: bool | None = None
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True)
class ApproveUserInput:
    admin_user_id: UUID
    target_user_id: UUID
    role: str | None = None
    plan_id: UUID | None = None
    access_days: int | None = None
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True)
class ExtendUserAccessInput:
    admin_user_id: UUID
    target_user_id: UUID
    plan_id: UUID
    access_days: int
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True)
class AccessLogOutput:
    id: UUID
    user_id: UUID | None
    action: str
    ip_address: str | None
    user_agent: str | None
    metadata: dict
    created_at: datetime
