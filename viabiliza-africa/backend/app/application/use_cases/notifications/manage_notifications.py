from uuid import UUID

from app.application.services.notification_service import NotificationService
from app.domain.repositories.notification_repository import INotificationRepository


def _to_output(n) -> dict:
    meta = n.metadata if isinstance(n.metadata, dict) else {}
    return {
        "id": str(n.id),
        "type": n.type,
        "title": n.title,
        "body": n.body,
        "href": n.href,
        "project_id": str(n.project_id) if n.project_id else None,
        "metadata": meta,
        "is_read": n.is_read,
        "created_at": n.created_at.isoformat(),
    }


class ListNotificationsUseCase:
    def __init__(
        self,
        notification_repository: INotificationRepository,
    ) -> None:
        self._repo = notification_repository

    def execute(
        self,
        *,
        user_id: UUID,
        limit: int = 40,
        offset: int = 0,
        unread_only: bool = False,
    ) -> dict:
        items = self._repo.find_for_user(
            user_id, limit=min(limit, 100), offset=offset, unread_only=unread_only
        )
        return {
            "items": [_to_output(n) for n in items],
            "total": len(items),
            "unread_count": self._repo.count_unread(user_id),
        }


class MarkNotificationReadUseCase:
    def __init__(self, notification_repository: INotificationRepository) -> None:
        self._repo = notification_repository

    def execute(self, *, user_id: UUID, notification_id: UUID) -> dict:
        self._repo.mark_read(user_id, notification_id)
        return {"message": "ok", "unread_count": self._repo.count_unread(user_id)}


class MarkAllNotificationsReadUseCase:
    def __init__(self, notification_repository: INotificationRepository) -> None:
        self._repo = notification_repository

    def execute(self, *, user_id: UUID) -> dict:
        count = self._repo.mark_all_read(user_id)
        return {"marked": count, "unread_count": 0}
