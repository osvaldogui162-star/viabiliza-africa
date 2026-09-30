from datetime import datetime, timezone
from uuid import UUID

from supabase import Client

from app.domain.repositories.registration_invite_repository import (
    IRegistrationInviteRepository,
    RegistrationInvite,
)
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


def _map(row: dict) -> RegistrationInvite:
    return RegistrationInvite(
        id=UUID(row["id"]),
        email=row["email"],
        role=row["role"],
        invited_by=UUID(row["invited_by"]) if row.get("invited_by") else None,
        project_id=UUID(row["project_id"]) if row.get("project_id") else None,
        permission=row.get("permission") or "view",
        source=row.get("source") or "project_share",
        expires_at=datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00")),
        consumed_at=(
            datetime.fromisoformat(row["consumed_at"].replace("Z", "+00:00"))
            if row.get("consumed_at")
            else None
        ),
        created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
        capabilities=row.get("capabilities") or {},
        office_member_id=(
            UUID(row["office_member_id"]) if row.get("office_member_id") else None
        ),
        job_title=row.get("job_title"),
    )


class SupabaseRegistrationInviteRepository(IRegistrationInviteRepository):
    TABLE = "user_registration_invites"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_pending_for_email(self, email: str) -> list[RegistrationInvite]:
        now = datetime.now(timezone.utc).isoformat()
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("email", email.lower())
            .is_("consumed_at", "null")
            .gt("expires_at", now)
            .order("created_at", desc=True)
            .execute()
        )
        return [_map(r) for r in get_rows(response)]

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
        payload = {
            "email": email.lower(),
            "role": role,
            "invited_by": str(invited_by) if invited_by else None,
            "project_id": str(project_id) if project_id else None,
            "permission": permission,
            "source": source,
            "expires_at": expires_at.isoformat(),
            "capabilities": capabilities or {},
            "office_member_id": str(office_member_id) if office_member_id else None,
            "job_title": job_title,
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        if not row:
            raise RuntimeError("Falha ao criar convite de registo")
        return _map(row)

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
        normalized = email.lower()
        now = datetime.now(timezone.utc).isoformat()
        existing = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("email", normalized)
            .eq("project_id", str(project_id))
            .eq("source", "project_share")
            .is_("consumed_at", "null")
            .gt("expires_at", now)
            .limit(1)
            .execute()
        )
        rows = get_rows(existing)
        payload = {
            "permission": permission,
            "invited_by": str(invited_by),
            "expires_at": expires_at.isoformat(),
            "capabilities": capabilities or {},
            "office_member_id": str(office_member_id) if office_member_id else None,
            "job_title": job_title,
        }
        if rows:
            invite_id = rows[0]["id"]
            self._client.table(self.TABLE).update(payload).eq("id", invite_id).execute()
            refetch = (
                self._client.table(self.TABLE).select("*").eq("id", invite_id).limit(1).execute()
            )
            ref_rows = get_rows(refetch)
            if not ref_rows:
                raise RuntimeError("Falha ao actualizar convite de registo")
            return _map(ref_rows[0])
        return self.create(
            email=normalized,
            role="user",
            invited_by=invited_by,
            project_id=project_id,
            permission=permission,
            source="project_share",
            expires_at=expires_at,
            capabilities=capabilities,
            office_member_id=office_member_id,
            job_title=job_title,
        )

    def consume(self, invite_id: UUID, user_id: UUID) -> None:
        self._client.table(self.TABLE).update(
            {
                "consumed_at": datetime.now(timezone.utc).isoformat(),
                "consumed_by": str(user_id),
            }
        ).eq("id", str(invite_id)).execute()
