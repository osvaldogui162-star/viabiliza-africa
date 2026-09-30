from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.project_share import ProjectShare
from app.domain.enums.share_permission import SharePermission


class IProjectShareRepository(ABC):
    """Interface do repositório de partilhas de projeto."""

    @abstractmethod
    def find_by_project_and_user(
        self, project_id: UUID, user_id: UUID
    ) -> ProjectShare | None:
        ...

    @abstractmethod
    def find_by_project(self, project_id: UUID) -> list[ProjectShare]:
        ...

    @abstractmethod
    def count_by_project(self, project_id: UUID) -> int:
        ...

    @abstractmethod
    def count_by_projects(self, project_ids: list[UUID]) -> dict[UUID, int]:
        ...

    @abstractmethod
    def find_shared_project_ids(
        self, user_id: UUID, project_ids: list[UUID]
    ) -> set[UUID]:
        ...

    @abstractmethod
    def find_project_ids_for_user(self, user_id: UUID) -> list[UUID]:
        ...

    @abstractmethod
    def create(
        self,
        *,
        project_id: UUID,
        user_id: UUID,
        shared_by: UUID,
        permission: SharePermission,
        office_member_id: UUID | None = None,
        job_title: str | None = None,
        capabilities: dict[str, bool] | None = None,
    ) -> ProjectShare:
        ...

    @abstractmethod
    def update(
        self,
        project_id: UUID,
        user_id: UUID,
        *,
        permission: SharePermission | None = None,
        office_member_id: UUID | None = None,
        job_title: str | None = None,
        capabilities: dict[str, bool] | None = None,
    ) -> ProjectShare:
        ...

    @abstractmethod
    def find_by_office_member(self, office_member_id: UUID) -> list[ProjectShare]:
        ...

    @abstractmethod
    def project_ids_by_office_members(
        self, office_member_ids: list[UUID]
    ) -> dict[UUID, list[UUID]]:
        ...

    @abstractmethod
    def delete(self, project_id: UUID, user_id: UUID) -> None:
        ...
