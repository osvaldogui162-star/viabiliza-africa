from uuid import UUID

from flask import Blueprint, g, jsonify, request
from marshmallow import ValidationError as MarshmallowValidationError

from app.di.container import Container
from app.domain.enums.user_role import UserRole
from app.presentation.decorators.rbac import require_auth, require_roles
from app.presentation.schemas.collaboration_schemas import (
    CreateTaskDependencySchema,
    CreateTaskSchema,
    MoveTaskSchema,
    SendChatMessageSchema,
    UpdateTaskSchema,
)
from app.presentation.serializers import to_dict


collaboration_bp = Blueprint("collaboration", __name__, url_prefix="/api/v1/projects")


def _validation_error(exc: MarshmallowValidationError):
    return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400


# ---------------------------------------------------------------------------
# Kanban — Integração Trello
# ---------------------------------------------------------------------------


@collaboration_bp.get("/<uuid:project_id>/kanban")
@require_auth
def get_kanban_integration(project_id: UUID):
    """Metadados do board Kanban externo (Trello) para embed."""
    container: Container = collaboration_bp.container  # type: ignore[attr-defined]
    result = container.get_kanban_integration_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
    )
    return jsonify(result), 200


@collaboration_bp.post("/<uuid:project_id>/kanban/sync")
@require_auth
def sync_kanban_board(project_id: UUID):
    """Sincronizar cartões do Trello para a API."""
    container: Container = collaboration_bp.container  # type: ignore[attr-defined]
    result = container.sync_kanban_board_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
    )
    return jsonify(result), 200


# ---------------------------------------------------------------------------
# Kanban — Tarefas (UC24, UC25)
# ---------------------------------------------------------------------------


@collaboration_bp.get("/<uuid:project_id>/tasks")
@require_auth
def list_tasks(project_id: UUID):
    container: Container = collaboration_bp.container  # type: ignore[attr-defined]
    grouped = request.args.get("grouped", "true").lower() != "false"
    sync = request.args.get("sync", "true").lower() != "false"
    result = container.list_tasks_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        status=request.args.get("status"),
        grouped=grouped,
        sync=sync,
    )
    return jsonify(result), 200


@collaboration_bp.post("/<uuid:project_id>/tasks")
@require_auth
def create_task(project_id: UUID):
    """UC24 — Criar tarefa no Kanban."""
    try:
        data = CreateTaskSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = collaboration_bp.container  # type: ignore[attr-defined]
    result = container.create_task_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        title=data["title"],
        description=data.get("description"),
        assignee_id=data.get("assignee_id"),
        due_date=data.get("due_date"),
    )
    return jsonify(to_dict(result)), 201


@collaboration_bp.get("/<uuid:project_id>/tasks/dependencies")
@require_auth
def list_dependencies(project_id: UUID):
    container: Container = collaboration_bp.container  # type: ignore[attr-defined]
    result = container.list_task_dependencies_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
    )
    return jsonify(result), 200


@collaboration_bp.post("/<uuid:project_id>/tasks/dependencies")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def create_dependency(project_id: UUID):
    """UC26 — Criar dependência entre tarefas."""
    try:
        data = CreateTaskDependencySchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = collaboration_bp.container  # type: ignore[attr-defined]
    result = container.create_task_dependency_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        predecessor_task_id=data["predecessor_task_id"],
        successor_task_id=data["successor_task_id"],
    )
    return jsonify(to_dict(result)), 201


@collaboration_bp.delete("/<uuid:project_id>/tasks/dependencies/<uuid:dependency_id>")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def delete_dependency(project_id: UUID, dependency_id: UUID):
    container: Container = collaboration_bp.container  # type: ignore[attr-defined]
    result = container.delete_task_dependency_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        dependency_id=dependency_id,
    )
    return jsonify(result), 200


@collaboration_bp.get("/<uuid:project_id>/tasks/<uuid:task_id>")
@require_auth
def get_task(project_id: UUID, task_id: UUID):
    container: Container = collaboration_bp.container  # type: ignore[attr-defined]
    result = container.get_task_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        task_id=task_id,
    )
    return jsonify(to_dict(result)), 200


@collaboration_bp.patch("/<uuid:project_id>/tasks/<uuid:task_id>")
@require_auth
def update_task(project_id: UUID, task_id: UUID):
    try:
        data = UpdateTaskSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = collaboration_bp.container  # type: ignore[attr-defined]
    payload = {}
    if "title" in data:
        payload["title"] = data["title"]
    if "description" in data:
        payload["description"] = data["description"]
    if "assignee_id" in data:
        payload["assignee_id"] = data["assignee_id"]
    if "due_date" in data:
        payload["due_date"] = data["due_date"]

    result = container.update_task_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        task_id=task_id,
        **payload,
    )
    return jsonify(to_dict(result)), 200


@collaboration_bp.patch("/<uuid:project_id>/tasks/<uuid:task_id>/move")
@require_auth
def move_task(project_id: UUID, task_id: UUID):
    """UC25 — Mover tarefa (arrastar/soltar)."""
    try:
        data = MoveTaskSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = collaboration_bp.container  # type: ignore[attr-defined]
    result = container.move_task_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        task_id=task_id,
        status=data["status"],
        position=data.get("position"),
    )
    return jsonify(to_dict(result)), 200


@collaboration_bp.delete("/<uuid:project_id>/tasks/<uuid:task_id>")
@require_auth
def delete_task(project_id: UUID, task_id: UUID):
    container: Container = collaboration_bp.container  # type: ignore[attr-defined]
    result = container.delete_task_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        task_id=task_id,
    )
    return jsonify(result), 200


# ---------------------------------------------------------------------------
# Chat (UC27)
# ---------------------------------------------------------------------------


@collaboration_bp.get("/<uuid:project_id>/chat/messages")
@require_auth
def list_chat_messages(project_id: UUID):
    container: Container = collaboration_bp.container  # type: ignore[attr-defined]
    before_id = request.args.get("before_id")
    result = container.list_chat_messages_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        limit=int(request.args.get("limit", 50)),
        before_id=UUID(before_id) if before_id else None,
    )
    return jsonify(result), 200


@collaboration_bp.post("/<uuid:project_id>/chat/messages")
@require_auth
def send_chat_message(project_id: UUID):
    """UC27 — Enviar mensagem no chat."""
    try:
        data = SendChatMessageSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = collaboration_bp.container  # type: ignore[attr-defined]
    result = container.send_chat_message_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        content=data["content"],
    )
    return jsonify(to_dict(result)), 201
