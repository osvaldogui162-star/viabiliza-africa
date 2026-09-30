from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ProjectBillingIntegration:
    id: UUID
    project_id: UUID
    erp_label: str | None
    connection_status: str
    api_key_hint: str | None
    api_key_hash: str | None
    last_sync_at: datetime | None
    last_hash: str | None
    latest_snapshot: dict
    created_at: datetime
    updated_at: datetime
