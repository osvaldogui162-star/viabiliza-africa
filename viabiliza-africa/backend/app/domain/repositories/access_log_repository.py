from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.entities.access_log import AccessLog
from app.domain.enums.access_action import AccessAction


class IAccessLogRepository(ABC):
    """Interface do repositório de logs de acesso."""

    @abstractmethod
    def create(
        self,
        *,
        user_id: UUID | None,
        action: AccessAction,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict | None = None,
    ) -> AccessLog:
        ...

    @abstractmethod
    def find_all(
        self,
        *,
        user_id: UUID | None = None,
        action: AccessAction | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AccessLog]:
        ...

    @abstractmethod
    def count(
        self,
        *,
        user_id: UUID | None = None,
        action: AccessAction | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> int:
        ...
