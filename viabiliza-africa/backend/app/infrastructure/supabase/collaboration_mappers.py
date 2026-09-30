from datetime import date, datetime
from uuid import UUID

from app.domain.entities.collaboration import ChatMessage, KanbanTask, TaskDependency
from app.domain.enums.task_status import TaskStatus


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def map_kanban_task(row: dict) -> KanbanTask:
    due = row.get("due_date")
    return KanbanTask(
        id=UUID(row["id"]),
        project_id=UUID(row["project_id"]),
        title=row["title"],
        description=row.get("description"),
        assignee_id=UUID(row["assignee_id"]) if row.get("assignee_id") else None,
        due_date=date.fromisoformat(due) if due else None,
        status=TaskStatus(row["status"]),
        position=row["position"],
        created_by=UUID(row["created_by"]),
        created_at=_parse_dt(row["created_at"]),
        updated_at=_parse_dt(row["updated_at"]),
        external_id=row.get("external_id"),
        provider=row.get("provider", "local"),
    )


def map_task_dependency(row: dict) -> TaskDependency:
    return TaskDependency(
        id=UUID(row["id"]),
        project_id=UUID(row["project_id"]),
        predecessor_task_id=UUID(row["predecessor_task_id"]),
        successor_task_id=UUID(row["successor_task_id"]),
        created_by=UUID(row["created_by"]),
        created_at=_parse_dt(row["created_at"]),
    )


def map_chat_message(row: dict) -> ChatMessage:
    return ChatMessage(
        id=UUID(row["id"]),
        project_id=UUID(row["project_id"]),
        sender_id=UUID(row["sender_id"]),
        content=row["content"],
        created_at=_parse_dt(row["created_at"]),
    )
