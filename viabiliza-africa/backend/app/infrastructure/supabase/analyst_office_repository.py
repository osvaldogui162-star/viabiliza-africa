from uuid import UUID

from supabase import Client

from app.domain.entities.analyst_office_member import AnalystOfficeMember
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from app.domain.repositories.analyst_office_repository import IAnalystOfficeRepository
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


def _parse_dt(value: str):
    from datetime import datetime

    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _map_row(row: dict) -> AnalystOfficeMember:
    return AnalystOfficeMember(
        id=UUID(row["id"]),
        owner_id=UUID(row["owner_id"]),
        user_id=UUID(row["user_id"]) if row.get("user_id") else None,
        email=row["email"],
        full_name=row["full_name"],
        job_title=row.get("job_title") or "Colaborador",
        status=row.get("status") or "active",
        notes=row.get("notes"),
        created_at=_parse_dt(row["created_at"]),
        updated_at=_parse_dt(row["updated_at"]),
    )


class SupabaseAnalystOfficeRepository(IAnalystOfficeRepository):
    TABLE = "analyst_office_members"

    def __init__(self, client: Client) -> None:
        self._client = client

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
        payload = {
            "owner_id": str(owner_id),
            "email": email.strip().lower(),
            "full_name": full_name.strip(),
            "job_title": job_title.strip() or "Colaborador",
            "user_id": str(user_id) if user_id else None,
            "notes": notes,
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        if row is None:
            raise RuntimeError("Falha ao criar profissional do escritório")
        return _map_row(row)

    def find_by_id(self, member_id: UUID) -> AnalystOfficeMember | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("id", str(member_id))
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return _map_row(row) if row else None

    def find_by_owner(self, owner_id: UUID, *, include_archived: bool = False) -> list[AnalystOfficeMember]:
        query = self._client.table(self.TABLE).select("*").eq("owner_id", str(owner_id))
        if not include_archived:
            query = query.eq("status", "active")
        response = query.order("full_name").execute()
        return [_map_row(row) for row in get_rows(response)]

    def find_by_owner_and_email(self, owner_id: UUID, email: str) -> AnalystOfficeMember | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("owner_id", str(owner_id))
            .eq("email", email.strip().lower())
            .eq("status", "active")
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return _map_row(row) if row else None

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
        payload: dict = {}
        if full_name is not None:
            payload["full_name"] = full_name.strip()
        if job_title is not None:
            payload["job_title"] = job_title.strip()
        if notes is not None:
            payload["notes"] = notes
        if user_id is not None:
            payload["user_id"] = str(user_id)
        if status is not None:
            payload["status"] = status
        response = (
            self._client.table(self.TABLE)
            .update(payload)
            .eq("id", str(member_id))
            .execute()
        )
        row = get_single_row(response)
        if row is None:
            raise EntityNotFoundError("Profissional", str(member_id))
        return _map_row(row)

    def count_by_owner(self, owner_id: UUID) -> int:
        response = (
            self._client.table(self.TABLE)
            .select("id", count="exact")
            .eq("owner_id", str(owner_id))
            .eq("status", "active")
            .execute()
        )
        return int(response.count or 0)

    def list_all_summaries(self, *, limit: int = 200, offset: int = 0) -> list[dict]:
        response = (
            self._client.table(self.TABLE)
            .select("owner_id")
            .eq("status", "active")
            .execute()
        )
        counts: dict[str, int] = {}
        for row in get_rows(response):
            oid = row["owner_id"]
            counts[oid] = counts.get(oid, 0) + 1
        return [{"owner_id": oid, "active_members": n} for oid, n in counts.items()][offset : offset + limit]
