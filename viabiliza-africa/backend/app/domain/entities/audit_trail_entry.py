from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums.audit_action import AuditAction
from app.domain.enums.audit_entity_type import AuditEntityType


@dataclass
class AuditTrailEntry:
    id: UUID
    project_id: UUID
    entity_type: AuditEntityType
    entity_id: UUID
    action: AuditAction
    actor_id: UUID | None
    data_hash: str
    previous_hash: str | None
    ip_address: str | None
    metadata: dict
    created_at: datetime
