from datetime import datetime
from uuid import UUID

from supabase import Client

from app.domain.entities.notification import UserNotification
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from app.domain.repositories.notification_repository import INotificationRepository
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


def _map(row: dict) -> UserNotification:
    created_raw = row.get("created_at")
    if created_raw:
        created_at = datetime.fromisoformat(str(created_raw).replace("Z", "+00:00"))
    else:
        created_at = datetime.now()
    return UserNotification(
        id=UUID(row["id"]),
        user_id=UUID(row["user_id"]),
        type=row["type"],
        title=row["title"],
        body=row.get("body"),
        href=row.get("href"),
        project_id=UUID(row["project_id"]) if row.get("project_id") else None,
        metadata=row.get("metadata") or {},
        is_read=bool(row.get("is_read")),
        created_at=created_at,
    )


class SupabaseNotificationRepository(INotificationRepository):
    TABLE = "user_notifications"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_for_user(
        self, user_id: UUID, *, limit: int = 50, offset: int = 0, unread_only: bool = False
    ) -> list[UserNotification]:
        query = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("user_id", str(user_id))
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
        )
        if unread_only:
            query = query.eq("is_read", False)
        return [_map(r) for r in get_rows(query.execute())]

    def count_unread(self, user_id: UUID) -> int:
        response = (
            self._client.table(self.TABLE)
            .select("id", count="exact")
            .eq("user_id", str(user_id))
            .eq("is_read", False)
            .execute()
        )
        return response.count or 0

    def create(
        self,
        *,
        user_id: UUID,
        type: str,
        title: str,
        body: str | None = None,
        href: str | None = None,
        project_id: UUID | None = None,
        metadata: dict | None = None,
    ) -> UserNotification:
        payload = {
            "user_id": str(user_id),
            "type": type,
            "title": title,
            "body": body,
            "href": href,
            "project_id": str(project_id) if project_id else None,
            "metadata": metadata or {},
        }
        row = get_single_row(self._client.table(self.TABLE).insert(payload).execute())
        if not row:
            raise RuntimeError("Falha ao criar notificação")
        return _map(row)

    def mark_read(self, user_id: UUID, notification_id: UUID) -> None:
        response = (
            self._client.table(self.TABLE)
            .update({"is_read": True})
            .eq("id", str(notification_id))
            .eq("user_id", str(user_id))
            .execute()
        )
        if not get_single_row(response):
            raise EntityNotFoundError("Notificação", str(notification_id))

    def mark_all_read(self, user_id: UUID) -> int:
        unread = self.find_for_user(user_id, limit=500, unread_only=True)
        if not unread:
            return 0
        self._client.table(self.TABLE).update({"is_read": True}).eq("user_id", str(user_id)).eq(
            "is_read", False
        ).execute()
        return len(unread)
