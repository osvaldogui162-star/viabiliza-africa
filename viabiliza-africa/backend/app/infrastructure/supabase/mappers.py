from datetime import datetime
from uuid import UUID

from app.domain.entities.access_log import AccessLog
from app.domain.entities.user import User
from app.domain.enums.access_action import AccessAction
from app.domain.enums.user_role import UserRole


def _parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now()
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def map_user_row(row: dict) -> User:
    return User(
        id=UUID(row["id"]),
        email=row["email"],
        full_name=row["full_name"],
        role=UserRole(row["role"]),
        is_active=row["is_active"],
        password_hash=row.get("password_hash"),
        email_verified=row.get("email_verified", True),
        google_id=row.get("google_id"),
        auth_provider=row.get("auth_provider", "email"),
        preferred_currency=row.get("preferred_currency") or "AOA",
        bank_code=row.get("bank_code"),
        created_at=_parse_datetime(row.get("created_at")),
        updated_at=_parse_datetime(row.get("updated_at")),
    )


def map_access_log_row(row: dict) -> AccessLog:
    return AccessLog(
        id=UUID(row["id"]),
        user_id=UUID(row["user_id"]) if row.get("user_id") else None,
        action=AccessAction(row["action"]),
        ip_address=row.get("ip_address"),
        user_agent=row.get("user_agent"),
        metadata=row.get("metadata") or {},
        created_at=_parse_datetime(row.get("created_at")),
    )
