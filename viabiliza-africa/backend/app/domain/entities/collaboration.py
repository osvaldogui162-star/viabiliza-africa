from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from app.domain.enums.task_status import TaskStatus


@dataclass
class KanbanTask:
    id: UUID
    project_id: UUID
    title: str
    description: str | None
    assignee_id: UUID | None
    due_date: date | None
    status: TaskStatus
    position: int
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    external_id: str | None = None
    provider: str = "local"


@dataclass
class TaskDependency:
    id: UUID
    project_id: UUID
    predecessor_task_id: UUID
    successor_task_id: UUID
    created_by: UUID
    created_at: datetime


@dataclass
class ChatMessage:
    id: UUID
    project_id: UUID
    sender_id: UUID
    content: str
    created_at: datetime
