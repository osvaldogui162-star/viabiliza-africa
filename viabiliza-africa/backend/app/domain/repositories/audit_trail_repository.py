from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.entities.audit_trail_entry import AuditTrailEntry
from app.domain.enums.audit_action import AuditAction
from app.domain.enums.audit_entity_type import AuditEntityType


class IAuditTrailRepository(ABC):
    @abstractmethod
    def create(
        self,
        *,
        project_id: UUID,
        entity_type: AuditEntityType,
        entity_id: UUID,
        action: AuditAction,
        actor_id: UUID | None,
        data_hash: str,
        previous_hash: str | None = None,
        ip_address: str | None = None,
        metadata: dict | None = None,
    ) -> AuditTrailEntry:
        ...

    @abstractmethod
    def find_by_project(
        self,
        project_id: UUID,
        *,
        entity_type: AuditEntityType | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditTrailEntry]:
        ...

    @abstractmethod
    def count_by_project(
        self,
        project_id: UUID,
        *,
        entity_type: AuditEntityType | None = None,
    ) -> int:
        ...

    @abstractmethod
    def get_last_hash_for_entity(
        self, entity_type: AuditEntityType, entity_id: UUID
    ) -> str | None:
        ...

    @abstractmethod
    def find_global(
        self,
        *,
        project_id: UUID | None = None,
        actor_id: UUID | None = None,
        entity_type: AuditEntityType | None = None,
        action: AuditAction | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AuditTrailEntry]:
        ...

    @abstractmethod
    def count_global(
        self,
        *,
        project_id: UUID | None = None,
        actor_id: UUID | None = None,
        entity_type: AuditEntityType | None = None,
        action: AuditAction | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> int:
        ...
