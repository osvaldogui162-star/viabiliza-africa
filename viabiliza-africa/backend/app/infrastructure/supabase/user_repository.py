from uuid import UUID

from supabase import Client

from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from app.domain.repositories.user_repository import IUserRepository
from app.infrastructure.supabase.mappers import map_user_row
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


class SupabaseUserRepository(IUserRepository):
    """Implementação concreta do repositório de utilizadores via Supabase."""

    TABLE = "users"
    RESET_TOKENS_TABLE = "password_reset_tokens"
    REFRESH_TOKENS_TABLE = "refresh_tokens"
    OTP_TABLE = "email_otp_codes"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_by_id(self, user_id: UUID) -> User | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("id", str(user_id))
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        if row is None:
            return None
        return map_user_row(row)

    def find_by_ids(self, user_ids: list[UUID]) -> dict[UUID, User]:
        if not user_ids:
            return {}
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .in_("id", [str(uid) for uid in user_ids])
            .execute()
        )
        return {UUID(row["id"]): map_user_row(row) for row in get_rows(response)}

    def find_by_google_id(self, google_id: str) -> User | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("google_id", google_id)
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        if row is None:
            return None
        return map_user_row(row)

    def find_by_email(self, email: str) -> User | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("email", email.lower())
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        if row is None:
            return None
        return map_user_row(row)

    def find_all(
        self,
        *,
        role: UserRole | None = None,
        is_active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[User]:
        query = self._client.table(self.TABLE).select("*")
        if role is not None:
            query = query.eq("role", role.value)
        if is_active is not None:
            query = query.eq("is_active", is_active)
        response = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        return [map_user_row(row) for row in get_rows(response)]

    def count(
        self,
        *,
        role: UserRole | None = None,
        is_active: bool | None = None,
    ) -> int:
        query = self._client.table(self.TABLE).select("id", count="exact")
        if role is not None:
            query = query.eq("role", role.value)
        if is_active is not None:
            query = query.eq("is_active", is_active)
        response = query.execute()
        return response.count or 0

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
        from datetime import datetime, timezone

        payload = {
            "email": email.lower(),
            "full_name": full_name,
            "role": role.value,
            "is_active": is_active,
            "email_verified": email_verified,
            "auth_provider": auth_provider,
        }
        if terms_accepted_at:
            payload["terms_accepted_at"] = terms_accepted_at
        if terms_version:
            payload["terms_version"] = terms_version
        if password_hash is not None:
            payload["password_hash"] = password_hash
        if google_id is not None:
            payload["google_id"] = google_id
        if bank_code is not None:
            payload["bank_code"] = bank_code.lower()
        if email_verified:
            payload["email_verified_at"] = datetime.now(timezone.utc).isoformat()
        response = self._client.table(self.TABLE).insert(payload).execute()
        rows = get_rows(response)
        if not rows:
            raise RuntimeError("Falha ao criar utilizador")
        return map_user_row(rows[0])

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
        bank_code: str | None = None,
        terms_accepted_at: str | None = None,
        terms_version: str | None = None,
    ) -> User:
        from datetime import datetime, timezone

        payload: dict = {}
        if full_name is not None:
            payload["full_name"] = full_name
        if role is not None:
            payload["role"] = role.value
        if is_active is not None:
            payload["is_active"] = is_active
        if password_hash is not None:
            payload["password_hash"] = password_hash
        if google_id is not None:
            payload["google_id"] = google_id
        if auth_provider is not None:
            payload["auth_provider"] = auth_provider
        if email_verified is not None:
            payload["email_verified"] = email_verified
            if email_verified:
                payload["email_verified_at"] = datetime.now(timezone.utc).isoformat()
        if preferred_currency is not None:
            payload["preferred_currency"] = preferred_currency
        if bank_code is not None:
            payload["bank_code"] = bank_code.lower() if bank_code else None
        if terms_accepted_at is not None:
            payload["terms_accepted_at"] = terms_accepted_at
        if terms_version is not None:
            payload["terms_version"] = terms_version

        if not payload:
            user = self.find_by_id(user_id)
            if user is None:
                raise EntityNotFoundError("Utilizador", str(user_id))
            return user

        response = (
            self._client.table(self.TABLE)
            .update(payload)
            .eq("id", str(user_id))
            .execute()
        )
        rows = get_rows(response)
        if not rows:
            raise EntityNotFoundError("Utilizador", str(user_id))
        return map_user_row(rows[0])

    def save_password_reset_token(
        self,
        user_id: UUID,
        token_hash: str,
        expires_at: str,
    ) -> None:
        self._client.table(self.RESET_TOKENS_TABLE).delete().eq(
            "user_id", str(user_id)
        ).execute()
        self._client.table(self.RESET_TOKENS_TABLE).insert(
            {
                "user_id": str(user_id),
                "token_hash": token_hash,
                "expires_at": expires_at,
            }
        ).execute()

    def find_by_password_reset_token(self, token_hash: str) -> User | None:
        from datetime import datetime, timezone

        response = (
            self._client.table(self.RESET_TOKENS_TABLE)
            .select("user_id, expires_at")
            .eq("token_hash", token_hash)
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        if row is None:
            return None

        expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
        if expires_at < datetime.now(timezone.utc):
            return None

        return self.find_by_id(UUID(row["user_id"]))

    def clear_password_reset_token(self, user_id: UUID) -> None:
        self._client.table(self.RESET_TOKENS_TABLE).delete().eq(
            "user_id", str(user_id)
        ).execute()

    def save_refresh_token(
        self,
        user_id: UUID,
        token_hash: str,
        expires_at: str,
    ) -> None:
        self._client.table(self.REFRESH_TOKENS_TABLE).insert(
            {
                "user_id": str(user_id),
                "token_hash": token_hash,
                "expires_at": expires_at,
            }
        ).execute()

    def find_by_refresh_token(self, token_hash: str) -> User | None:
        from datetime import datetime, timezone

        response = (
            self._client.table(self.REFRESH_TOKENS_TABLE)
            .select("user_id, expires_at")
            .eq("token_hash", token_hash)
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        if row is None:
            return None

        expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
        if expires_at < datetime.now(timezone.utc):
            self.revoke_refresh_token(token_hash)
            return None

        return self.find_by_id(UUID(row["user_id"]))

    def revoke_refresh_token(self, token_hash: str) -> None:
        self._client.table(self.REFRESH_TOKENS_TABLE).delete().eq(
            "token_hash", token_hash
        ).execute()

    def revoke_all_refresh_tokens(self, user_id: UUID) -> None:
        self._client.table(self.REFRESH_TOKENS_TABLE).delete().eq(
            "user_id", str(user_id)
        ).execute()

    def save_signup_otp(
        self,
        *,
        email: str,
        code_hash: str,
        full_name: str,
        password_hash: str,
        expires_at: str,
    ) -> None:
        normalized = email.strip().lower()
        self._client.table(self.OTP_TABLE).delete().eq("email", normalized).eq(
            "purpose", "signup"
        ).is_("consumed_at", "null").execute()
        self._client.table(self.OTP_TABLE).insert(
            {
                "email": normalized,
                "purpose": "signup",
                "code_hash": code_hash,
                "full_name": full_name.strip(),
                "password_hash": password_hash,
                "expires_at": expires_at,
            }
        ).execute()

    def find_pending_signup_otp(self, email: str) -> dict | None:
        from datetime import datetime, timezone

        response = (
            self._client.table(self.OTP_TABLE)
            .select("*")
            .eq("email", email.strip().lower())
            .eq("purpose", "signup")
            .is_("consumed_at", "null")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        if row is None:
            return None
        expires_at = datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00"))
        if expires_at < datetime.now(timezone.utc):
            return None
        return row

    def increment_signup_otp_attempts(self, otp_id: UUID) -> int:
        row = get_single_row(
            self._client.table(self.OTP_TABLE)
            .select("attempts")
            .eq("id", str(otp_id))
            .limit(1)
            .execute()
        )
        if row is None:
            return 0
        attempts = int(row["attempts"]) + 1
        self._client.table(self.OTP_TABLE).update({"attempts": attempts}).eq(
            "id", str(otp_id)
        ).execute()
        return attempts

    def consume_signup_otp(self, otp_id: UUID) -> None:
        from datetime import datetime, timezone

        self._client.table(self.OTP_TABLE).update(
            {"consumed_at": datetime.now(timezone.utc).isoformat()}
        ).eq("id", str(otp_id)).execute()

    def latest_signup_otp_created_at(self, email: str) -> str | None:
        response = (
            self._client.table(self.OTP_TABLE)
            .select("created_at")
            .eq("email", email.strip().lower())
            .eq("purpose", "signup")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return row["created_at"] if row else None
