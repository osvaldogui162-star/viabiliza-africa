from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole


class IUserRepository(ABC):
    """Interface do repositório de utilizadores (Dependency Inversion)."""

    @abstractmethod
    def find_by_id(self, user_id: UUID) -> User | None:
        ...

    @abstractmethod
    def find_by_ids(self, user_ids: list[UUID]) -> dict[UUID, User]:
        ...

    @abstractmethod
    def find_by_google_id(self, google_id: str) -> User | None:
        ...

    @abstractmethod
    def find_by_email(self, email: str) -> User | None:
        ...

    @abstractmethod
    def find_all(
        self,
        *,
        role: UserRole | None = None,
        is_active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[User]:
        ...

    @abstractmethod
    def count(
        self,
        *,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> int:
        ...

    @abstractmethod
    def create(
        self,
        *,
        email: str,
        full_name: str,
        role: UserRole,
        password_hash: str | None = None,
        google_id: str | None = None,
        auth_provider: str = "email",
        email_verified: bool = False,
        is_active: bool = True,
        bank_code: str | None = None,
        terms_accepted_at: str | None = None,
        terms_version: str | None = None,
    ) -> User:
        ...

    @abstractmethod
    def save_signup_otp(
        self,
        *,
        email: str,
        code_hash: str,
        full_name: str,
        password_hash: str,
        expires_at: str,
    ) -> None:
        ...

    @abstractmethod
    def find_pending_signup_otp(self, email: str) -> dict | None:
        ...

    @abstractmethod
    def increment_signup_otp_attempts(self, otp_id: UUID) -> int:
        ...

    @abstractmethod
    def consume_signup_otp(self, otp_id: UUID) -> None:
        ...

    @abstractmethod
    def latest_signup_otp_created_at(self, email: str) -> str | None:
        ...

    @abstractmethod
    def update(
        self,
        user_id: UUID,
        *,
        full_name: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
        password_hash: str | None = None,
        google_id: str | None = None,
        auth_provider: str | None = None,
        email_verified: bool | None = None,
        preferred_currency: str | None = None,
        terms_accepted_at: str | None = None,
        terms_version: str | None = None,
    ) -> User:
        ...

    @abstractmethod
    def save_password_reset_token(
        self,
        user_id: UUID,
        token_hash: str,
        expires_at: str,
    ) -> None:
        ...

    @abstractmethod
    def find_by_password_reset_token(self, token_hash: str) -> User | None:
        ...

    @abstractmethod
    def clear_password_reset_token(self, user_id: UUID) -> None:
        ...

    @abstractmethod
    def save_refresh_token(
        self,
        user_id: UUID,
        token_hash: str,
        expires_at: str,
    ) -> None:
        ...

    @abstractmethod
    def find_by_refresh_token(self, token_hash: str) -> User | None:
        ...

    @abstractmethod
    def revoke_refresh_token(self, token_hash: str) -> None:
        ...

    @abstractmethod
    def revoke_all_refresh_tokens(self, user_id: UUID) -> None:
        ...
