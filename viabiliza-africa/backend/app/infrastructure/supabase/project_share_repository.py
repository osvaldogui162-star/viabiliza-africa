from uuid import UUID

from supabase import Client

from app.domain.entities.project_share import ProjectShare
from app.domain.enums.share_permission import SharePermission
from app.domain.repositories.project_share_repository import IProjectShareRepository
from app.infrastructure.supabase.project_mappers import map_project_share_row
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


class SupabaseProjectShareRepository(IProjectShareRepository):
    """Implementação Supabase do repositório de partilhas."""

    TABLE = "project_shares"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_by_project_and_user(
        self, project_id: UUID, user_id: UUID
    ) -> ProjectShare | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("project_id", str(project_id))
            .eq("user_id", str(user_id))
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return map_project_share_row(row) if row else None

    def find_by_project(self, project_id: UUID) -> list[ProjectShare]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("project_id", str(project_id))
            .order("created_at", desc=False)
            .execute()
        )
        return [map_project_share_row(row) for row in get_rows(response)]

    def count_by_project(self, project_id: UUID) -> int:
        response = (
            self._client.table(self.TABLE)
            .select("id", count="exact")
            .eq("project_id", str(project_id))
            .execute()
        )
        return response.count or 0

    def count_by_projects(self, project_ids: list[UUID]) -> dict[UUID, int]:
        if not project_ids:
            return {}
        response = (
            self._client.table(self.TABLE)
            .select("project_id")
            .in_("project_id", [str(pid) for pid in project_ids])
            .execute()
        )
        counts = {pid: 0 for pid in project_ids}
        for row in get_rows(response):
            pid = UUID(row["project_id"])
            counts[pid] = counts.get(pid, 0) + 1
        return counts

    def find_shared_project_ids(
        self, user_id: UUID, project_ids: list[UUID]
    ) -> set[UUID]:
        if not project_ids:
            return set()
        response = (
            self._client.table(self.TABLE)
            .select("project_id")
            .eq("user_id", str(user_id))
            .in_("project_id", [str(pid) for pid in project_ids])
            .execute()
        )
        return {UUID(row["project_id"]) for row in get_rows(response)}

    def find_project_ids_for_user(self, user_id: UUID) -> list[UUID]:
        response = (
            self._client.table(self.TABLE)
            .select("project_id")
            .eq("user_id", str(user_id))
            .execute()
        )
        return [UUID(row["project_id"]) for row in get_rows(response)]

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
        payload = {
            "project_id": str(project_id),
            "user_id": str(user_id),
            "shared_by": str(shared_by),
            "permission": permission.value,
            "office_member_id": str(office_member_id) if office_member_id else None,
            "job_title": job_title,
            "capabilities": capabilities or {},
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        rows = get_rows(response)
        if not rows:
            raise RuntimeError("Falha ao partilhar projeto")
        return map_project_share_row(rows[0])

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
        payload: dict = {}
        if permission is not None:
            payload["permission"] = permission.value
        if office_member_id is not None:
            payload["office_member_id"] = str(office_member_id)
        if job_title is not None:
            payload["job_title"] = job_title
        if capabilities is not None:
            payload["capabilities"] = capabilities
        response = (
            self._client.table(self.TABLE)
            .update(payload)
            .eq("project_id", str(project_id))
            .eq("user_id", str(user_id))
            .execute()
        )
        row = get_single_row(response)
        if row is None:
            from app.domain.exceptions.domain_exceptions import EntityNotFoundError

            raise EntityNotFoundError("Partilha", f"{project_id}:{user_id}")
        return map_project_share_row(row)

    def find_by_office_member(self, office_member_id: UUID) -> list[ProjectShare]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("office_member_id", str(office_member_id))
            .execute()
        )
        return [map_project_share_row(row) for row in get_rows(response)]

    def project_ids_by_office_members(
        self, office_member_ids: list[UUID]
    ) -> dict[UUID, list[UUID]]:
        if not office_member_ids:
            return {}
        response = (
            self._client.table(self.TABLE)
            .select("office_member_id,project_id")
            .in_("office_member_id", [str(mid) for mid in office_member_ids])
            .execute()
        )
        grouped: dict[UUID, list[UUID]] = {mid: [] for mid in office_member_ids}
        for row in get_rows(response):
            member_id = row.get("office_member_id")
            project_id = row.get("project_id")
            if not member_id or not project_id:
                continue
            mid = UUID(str(member_id))
            pid = UUID(str(project_id))
            grouped.setdefault(mid, []).append(pid)
        return grouped

    def delete(self, project_id: UUID, user_id: UUID) -> None:
        self._client.table(self.TABLE).delete().eq(
            "project_id", str(project_id)
        ).eq("user_id", str(user_id)).execute()
