from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums.user_role import UserRole


@dataclass
class User:
    """Entidade de domínio — utilizador da plataforma."""

    id: UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime
    password_hash: str | None = None
    email_verified: bool = True
    google_id: str | None = None
    auth_provider: str = "email"
    preferred_currency: str = "AOA"
    bank_code: str | None = None

    def can_manage_users(self) -> bool:
        return self.role == UserRole.ADMIN and self.is_active

    def can_view_access_logs(self) -> bool:
        return self.role == UserRole.ADMIN and self.is_active

    def can_manage_system_settings(self) -> bool:
        return self.role == UserRole.ADMIN and self.is_active

    def can_view_full_audit_trail(self) -> bool:
        return self.role == UserRole.ADMIN and self.is_active
