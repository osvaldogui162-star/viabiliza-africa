from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID


@dataclass
class UserNotification:
    id: UUID
    user_id: UUID
    type: str
    title: str
    body: str | None
    href: str | None
    project_id: UUID | None
    metadata: dict
    is_read: bool
    created_at: datetime
