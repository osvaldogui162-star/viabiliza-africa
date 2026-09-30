from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums.share_permission import SharePermission
from app.domain.services.share_capabilities import merge_capabilities


@dataclass
class ProjectShare:
    """Partilha de projeto com outro utilizador."""

    id: UUID
    project_id: UUID
    user_id: UUID
    shared_by: UUID
    permission: SharePermission
    office_member_id: UUID | None
    job_title: str | None
    capabilities: dict[str, bool]
    created_at: datetime

    def effective_capabilities(self) -> dict[str, bool]:
        return merge_capabilities(self.permission, self.capabilities or None)

    def allows(self, capability: str) -> bool:
        return bool(self.effective_capabilities().get(capability, False))
