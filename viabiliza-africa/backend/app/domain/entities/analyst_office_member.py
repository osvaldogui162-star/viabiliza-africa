from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class AnalystOfficeMember:
    id: UUID
    owner_id: UUID
    user_id: UUID | None
    email: str
    full_name: str
    job_title: str
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    @property
    def is_active(self) -> bool:
        return self.status == "active"
