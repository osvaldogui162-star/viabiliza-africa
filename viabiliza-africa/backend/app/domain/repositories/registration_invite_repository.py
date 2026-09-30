from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class RegistrationInvite:
    id: UUID
    email: str
    role: str
    invited_by: UUID | None
    project_id: UUID | None
    permission: str
    source: str
    expires_at: datetime
    consumed_at: datetime | None
    created_at: datetime
    capabilities: dict | None = None
    office_member_id: UUID | None = None
    job_title: str | None = None


class IRegistrationInviteRepository(ABC):
    @abstractmethod
    def find_pending_for_email(self, email: str) -> list[RegistrationInvite]:
        ...

    @abstractmethod
    def create(
        self,
        *,
        email: str,
        role: str,
        invited_by: UUID | None,
        project_id: UUID | None,
        permission: str,
        source: str,
        expires_at: datetime,
        capabilities: dict | None = None,
        office_member_id: UUID | None = None,
        job_title: str | None = None,
    ) -> RegistrationInvite:
        ...

    @abstractmethod
    def upsert_pending_project_share(
        self,
        *,
        email: str,
        invited_by: UUID,
        project_id: UUID,
        permission: str,
        expires_at: datetime,
        capabilities: dict | None = None,
        office_member_id: UUID | None = None,
        job_title: str | None = None,
    ) -> RegistrationInvite:
        ...

    @abstractmethod
    def consume(self, invite_id: UUID, user_id: UUID) -> None:
        ...
