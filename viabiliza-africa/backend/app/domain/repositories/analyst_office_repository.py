from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.analyst_office_member import AnalystOfficeMember


class IAnalystOfficeRepository(ABC):
    @abstractmethod
    def create(
        self,
        *,
        owner_id: UUID,
        email: str,
        full_name: str,
        job_title: str,
        user_id: UUID | None = None,
        notes: str | None = None,
    ) -> AnalystOfficeMember:
        ...

    @abstractmethod
    def find_by_id(self, member_id: UUID) -> AnalystOfficeMember | None:
        ...

    @abstractmethod
    def find_by_owner(self, owner_id: UUID, *, include_archived: bool = False) -> list[AnalystOfficeMember]:
        ...

    @abstractmethod
    def find_by_owner_and_email(self, owner_id: UUID, email: str) -> AnalystOfficeMember | None:
        ...

    @abstractmethod
    def update(
        self,
        member_id: UUID,
        *,
        full_name: str | None = None,
        job_title: str | None = None,
        notes: str | None = None,
        user_id: UUID | None = None,
        status: str | None = None,
    ) -> AnalystOfficeMember:
        ...

    @abstractmethod
    def count_by_owner(self, owner_id: UUID) -> int:
        ...

    @abstractmethod
    def list_all_summaries(self, *, limit: int = 200, offset: int = 0) -> list[dict]:
        """Admin: analistas com contagens de equipa."""
