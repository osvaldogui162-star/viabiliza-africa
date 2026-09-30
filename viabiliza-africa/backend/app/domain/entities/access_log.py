from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums.access_action import AccessAction


@dataclass
class AccessLog:
    """Registo imutável de acesso ou ação sensível."""

    id: UUID
    user_id: UUID | None
    action: AccessAction
    ip_address: str | None
    user_agent: str | None
    metadata: dict
    created_at: datetime
