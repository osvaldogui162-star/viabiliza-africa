from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from app.domain.entities.collaboration import ChatMessage, KanbanTask, TaskDependency
from app.domain.enums.task_status import TaskStatus


class IKanbanTaskRepository(ABC):
    @abstractmethod
    def find_by_id(self, task_id: UUID) -> KanbanTask | None:
        ...

    @abstractmethod
    def find_by_external_id(self, project_id: UUID, external_id: str) -> KanbanTask | None:
        ...

    @abstractmethod
    def find_by_project(
        self, project_id: UUID, *, status: TaskStatus | None = None
    ) -> list[KanbanTask]:
        ...

    @abstractmethod
    def create(
        self,
        *,
        project_id: UUID,
        title: str,
        description: str | None,
        assignee_id: UUID | None,
        due_date: date | None,
        status: TaskStatus,
        position: int,
        created_by: UUID,
        external_id: str | None = None,
        provider: str = "local",
    ) -> KanbanTask:
        ...

    @abstractmethod
    def update(
        self,
        task_id: UUID,
        *,
        title: str | None = None,
        description: str | None = None,
        assignee_id: UUID | None = ...,  # type: ignore[assignment]
        due_date: date | None = ...,  # type: ignore[assignment]
        status: TaskStatus | None = None,
        position: int | None = None,
        external_id: str | None = None,
        provider: str | None = None,
    ) -> KanbanTask:
        ...

    @abstractmethod
    def delete(self, task_id: UUID) -> None:
        ...

    @abstractmethod
    def max_position(self, project_id: UUID, status: TaskStatus) -> int:
        ...


class ITaskDependencyRepository(ABC):
    @abstractmethod
    def find_by_id(self, dependency_id: UUID) -> TaskDependency | None:
        ...

    @abstractmethod
    def find_by_project(self, project_id: UUID) -> list[TaskDependency]:
        ...

    @abstractmethod
    def find_predecessors(self, task_id: UUID) -> list[TaskDependency]:
        ...

    @abstractmethod
    def find_successors(self, task_id: UUID) -> list[TaskDependency]:
        ...

    @abstractmethod
    def exists(self, predecessor_id: UUID, successor_id: UUID) -> bool:
        ...

    @abstractmethod
    def create(
        self,
        *,
        project_id: UUID,
        predecessor_task_id: UUID,
        successor_task_id: UUID,
        created_by: UUID,
    ) -> TaskDependency:
        ...

    @abstractmethod
    def delete(self, dependency_id: UUID) -> None:
        ...


class IChatMessageRepository(ABC):
    @abstractmethod
    def find_by_project(
        self, project_id: UUID, *, limit: int = 50, before_id: UUID | None = None
    ) -> list[ChatMessage]:
        ...

    @abstractmethod
    def find_after(
        self, project_id: UUID, after_id: UUID | None, *, limit: int = 50
    ) -> list[ChatMessage]:
        ...

    @abstractmethod
    def create(
        self,
        *,
        project_id: UUID,
        sender_id: UUID,
        content: str,
    ) -> ChatMessage:
        ...


class IChatReadStateRepository(ABC):
    @abstractmethod
    def upsert_read(
        self, *, user_id: UUID, project_id: UUID, message_id: UUID | None
    ) -> None:
        ...

    @abstractmethod
    def get_read_states(
        self, project_id: UUID, user_ids: list[UUID]
    ) -> dict[UUID, UUID | None]:
        ...


class IProjectPresenceRepository(ABC):
    @abstractmethod
    def heartbeat(self, *, user_id: UUID, project_id: UUID) -> None:
        ...

    @abstractmethod
    def list_online(
        self, project_id: UUID, *, within_seconds: int = 90
    ) -> list[UUID]:
        ...
