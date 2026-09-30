from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.billing_integration import ProjectBillingIntegration


class IProjectBillingIntegrationRepository(ABC):
    @abstractmethod
    def find_by_project(self, project_id: UUID) -> ProjectBillingIntegration | None:
        ...

    @abstractmethod
    def find_by_projects(self, project_ids: list[UUID]) -> dict[UUID, ProjectBillingIntegration]:
        ...

    @abstractmethod
    def find_by_api_key_hash(self, api_key_hash: str) -> ProjectBillingIntegration | None:
        ...

    @abstractmethod
    def upsert(
        self,
        *,
        project_id: UUID,
        erp_label: str | None = None,
        connection_status: str | None = None,
        api_key_hint: str | None = None,
        api_key_hash: str | None = None,
    ) -> ProjectBillingIntegration:
        ...

    @abstractmethod
    def record_sync(
        self,
        *,
        project_id: UUID,
        payload: dict,
        payload_hash: str,
        connection_status: str = "active",
    ) -> ProjectBillingIntegration:
        ...
