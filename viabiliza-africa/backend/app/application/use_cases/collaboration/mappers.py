from app.domain.entities.collaboration import ChatMessage, KanbanTask, TaskDependency
from app.domain.enums.task_status import TaskStatus


def to_task_output(task: KanbanTask) -> dict:
    return {
        "id": str(task.id),
        "project_id": str(task.project_id),
        "title": task.title,
        "description": task.description,
        "assignee_id": str(task.assignee_id) if task.assignee_id else None,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "status": task.status.value,
        "status_label": task.status.label(),
        "position": task.position,
        "created_by": str(task.created_by),
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "external_id": task.external_id,
        "provider": task.provider,
    }


def to_dependency_output(dep: TaskDependency) -> dict:
    return {
        "id": str(dep.id),
        "project_id": str(dep.project_id),
        "predecessor_task_id": str(dep.predecessor_task_id),
        "successor_task_id": str(dep.successor_task_id),
        "created_by": str(dep.created_by),
        "created_at": dep.created_at.isoformat(),
    }


def to_chat_message_output(msg: ChatMessage, *, user_name: str | None = None) -> dict:
    return {
        "id": str(msg.id),
        "project_id": str(msg.project_id),
        "sender_id": str(msg.sender_id),
        "user_id": str(msg.sender_id),
        "user_name": user_name or "Utilizador",
        "content": msg.content,
        "created_at": msg.created_at.isoformat(),
    }


def group_tasks_by_status(tasks: list[KanbanTask]) -> dict:
    board = {s.value: [] for s in TaskStatus}
    for task in tasks:
        board[task.status.value].append(to_task_output(task))
    return board
