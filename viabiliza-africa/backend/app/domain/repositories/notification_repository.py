from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.notification import UserNotification


class INotificationRepository(ABC):
    @abstractmethod
    def find_for_user(
        self, user_id: UUID, *, limit: int = 50, offset: int = 0, unread_only: bool = False
    ) -> list[UserNotification]:
        ...

    @abstractmethod
    def count_unread(self, user_id: UUID) -> int:
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def mark_read(self, user_id: UUID, notification_id: UUID) -> None:
        ...

    @abstractmethod
    def mark_all_read(self, user_id: UUID) -> int:
        ...
