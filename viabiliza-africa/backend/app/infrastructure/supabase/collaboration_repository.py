from datetime import date
from uuid import UUID

from supabase import Client

from app.domain.entities.collaboration import ChatMessage, KanbanTask, TaskDependency
from app.domain.enums.task_status import TaskStatus
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from datetime import datetime, timedelta, timezone

from app.domain.repositories.collaboration_repository import (
    IChatMessageRepository,
    IChatReadStateRepository,
    IKanbanTaskRepository,
    IProjectPresenceRepository,
    ITaskDependencyRepository,
)
from app.infrastructure.supabase.collaboration_mappers import (
    map_chat_message,
    map_kanban_task,
    map_task_dependency,
)
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


class SupabaseKanbanTaskRepository(IKanbanTaskRepository):
    TABLE = "kanban_tasks"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_by_id(self, task_id: UUID) -> KanbanTask | None:
        response = (
            self._client.table(self.TABLE).select("*").eq("id", str(task_id)).limit(1).execute()
        )
        row = get_single_row(response)
        return map_kanban_task(row) if row else None

    def find_by_external_id(self, project_id: UUID, external_id: str) -> KanbanTask | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("project_id", str(project_id))
            .eq("external_id", external_id)
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return map_kanban_task(row) if row else None

    def find_by_project(
        self, project_id: UUID, *, status: TaskStatus | None = None
    ) -> list[KanbanTask]:
        query = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("project_id", str(project_id))
            .order("status")
            .order("position")
            .order("created_at")
        )
        if status:
            query = query.eq("status", status.value)
        response = query.execute()
        return [map_kanban_task(r) for r in get_rows(response)]

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
        payload = {
            "project_id": str(project_id),
            "title": title,
            "description": description,
            "assignee_id": str(assignee_id) if assignee_id else None,
            "due_date": due_date.isoformat() if due_date else None,
            "status": status.value,
            "position": position,
            "created_by": str(created_by),
            "external_id": external_id,
            "provider": provider,
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        return map_kanban_task(row)

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
        payload: dict = {}
        if title is not None:
            payload["title"] = title
        if description is not None:
            payload["description"] = description
        if assignee_id is not ...:
            payload["assignee_id"] = str(assignee_id) if assignee_id else None
        if due_date is not ...:
            payload["due_date"] = due_date.isoformat() if due_date else None
        if status is not None:
            payload["status"] = status.value
        if position is not None:
            payload["position"] = position
        if external_id is not None:
            payload["external_id"] = external_id
        if provider is not None:
            payload["provider"] = provider

        if not payload:
            task = self.find_by_id(task_id)
            if task is None:
                raise EntityNotFoundError("Tarefa", str(task_id))
            return task

        response = (
            self._client.table(self.TABLE).update(payload).eq("id", str(task_id)).execute()
        )
        row = get_single_row(response)
        if not row:
            raise EntityNotFoundError("Tarefa", str(task_id))
        return map_kanban_task(row)

    def delete(self, task_id: UUID) -> None:
        self._client.table(self.TABLE).delete().eq("id", str(task_id)).execute()

    def max_position(self, project_id: UUID, status: TaskStatus) -> int:
        response = (
            self._client.table(self.TABLE)
            .select("position")
            .eq("project_id", str(project_id))
            .eq("status", status.value)
            .order("position", desc=True)
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return row["position"] if row else -1


class SupabaseTaskDependencyRepository(ITaskDependencyRepository):
    TABLE = "task_dependencies"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_by_id(self, dependency_id: UUID) -> TaskDependency | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("id", str(dependency_id))
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return map_task_dependency(row) if row else None

    def find_by_project(self, project_id: UUID) -> list[TaskDependency]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("project_id", str(project_id))
            .order("created_at")
            .execute()
        )
        return [map_task_dependency(r) for r in get_rows(response)]

    def find_predecessors(self, task_id: UUID) -> list[TaskDependency]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("successor_task_id", str(task_id))
            .execute()
        )
        return [map_task_dependency(r) for r in get_rows(response)]

    def find_successors(self, task_id: UUID) -> list[TaskDependency]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("predecessor_task_id", str(task_id))
            .execute()
        )
        return [map_task_dependency(r) for r in get_rows(response)]

    def exists(self, predecessor_id: UUID, successor_id: UUID) -> bool:
        response = (
            self._client.table(self.TABLE)
            .select("id")
            .eq("predecessor_task_id", str(predecessor_id))
            .eq("successor_task_id", str(successor_id))
            .limit(1)
            .execute()
        )
        return get_single_row(response) is not None

    def create(
        self,
        *,
        project_id: UUID,
        predecessor_task_id: UUID,
        successor_task_id: UUID,
        created_by: UUID,
    ) -> TaskDependency:
        payload = {
            "project_id": str(project_id),
            "predecessor_task_id": str(predecessor_task_id),
            "successor_task_id": str(successor_task_id),
            "created_by": str(created_by),
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        return map_task_dependency(row)

    def delete(self, dependency_id: UUID) -> None:
        self._client.table(self.TABLE).delete().eq("id", str(dependency_id)).execute()


class SupabaseChatMessageRepository(IChatMessageRepository):
    TABLE = "project_chat_messages"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_by_project(
        self, project_id: UUID, *, limit: int = 50, before_id: UUID | None = None
    ) -> list[ChatMessage]:
        query = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("project_id", str(project_id))
            .order("created_at", desc=True)
            .limit(min(limit, 100))
        )
        if before_id:
            before = self._find_row(before_id)
            if before:
                query = query.lt("created_at", before["created_at"])
        response = query.execute()
        rows = get_rows(response)
        rows.reverse()
        return [map_chat_message(r) for r in rows]

    def find_after(
        self, project_id: UUID, after_id: UUID | None, *, limit: int = 50
    ) -> list[ChatMessage]:
        query = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("project_id", str(project_id))
            .order("created_at", desc=False)
            .limit(min(limit, 100))
        )
        if after_id:
            after = self._find_row(after_id)
            if after:
                query = query.gt("created_at", after["created_at"])
        response = query.execute()
        return [map_chat_message(r) for r in get_rows(response)]

    def create(
        self,
        *,
        project_id: UUID,
        sender_id: UUID,
        content: str,
    ) -> ChatMessage:
        payload = {
            "project_id": str(project_id),
            "sender_id": str(sender_id),
            "content": content.strip(),
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        return map_chat_message(row)

    def _find_row(self, message_id: UUID) -> dict | None:
        response = (
            self._client.table(self.TABLE)
            .select("created_at")
            .eq("id", str(message_id))
            .limit(1)
            .execute()
        )
        return get_single_row(response)


class SupabaseChatReadStateRepository(IChatReadStateRepository):
    TABLE = "project_chat_read_state"

    def __init__(self, client: Client) -> None:
        self._client = client

    def upsert_read(
        self, *, user_id: UUID, project_id: UUID, message_id: UUID | None
    ) -> None:
        payload = {
            "user_id": str(user_id),
            "project_id": str(project_id),
            "last_read_message_id": str(message_id) if message_id else None,
            "last_read_at": datetime.now(timezone.utc).isoformat(),
        }
        self._client.table(self.TABLE).upsert(payload).execute()

    def get_read_states(
        self, project_id: UUID, user_ids: list[UUID]
    ) -> dict[UUID, UUID | None]:
        if not user_ids:
            return {}
        response = (
            self._client.table(self.TABLE)
            .select("user_id, last_read_message_id")
            .eq("project_id", str(project_id))
            .in_("user_id", [str(u) for u in user_ids])
            .execute()
        )
        out: dict[UUID, UUID | None] = {}
        for row in get_rows(response):
            mid = row.get("last_read_message_id")
            out[UUID(row["user_id"])] = UUID(mid) if mid else None
        return out


class SupabaseProjectPresenceRepository(IProjectPresenceRepository):
    TABLE = "project_presence"

    def __init__(self, client: Client) -> None:
        self._client = client

    def heartbeat(self, *, user_id: UUID, project_id: UUID) -> None:
        payload = {
            "user_id": str(user_id),
            "project_id": str(project_id),
            "last_seen_at": datetime.now(timezone.utc).isoformat(),
        }
        self._client.table(self.TABLE).upsert(payload).execute()

    def list_online(
        self, project_id: UUID, *, within_seconds: int = 90
    ) -> list[UUID]:
        cutoff = (datetime.now(timezone.utc) - timedelta(seconds=within_seconds)).isoformat()
        response = (
            self._client.table(self.TABLE)
            .select("user_id")
            .eq("project_id", str(project_id))
            .gte("last_seen_at", cutoff)
            .execute()
        )
        return [UUID(r["user_id"]) for r in get_rows(response)]
