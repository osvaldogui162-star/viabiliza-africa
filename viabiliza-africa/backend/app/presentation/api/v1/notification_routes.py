from uuid import UUID

from flask import Blueprint, Response, g, jsonify, request, stream_with_context
import json
import time

from marshmallow import ValidationError as MarshmallowValidationError

from app.di.container import Container
from app.presentation.decorators.rbac import require_auth
from app.presentation.schemas.notification_schemas import MarkChatReadSchema, PresenceHeartbeatSchema


notifications_bp = Blueprint("notifications", __name__, url_prefix="/api/v1")


@notifications_bp.get("/notifications")
@require_auth
def list_notifications():
    container: Container = notifications_bp.container  # type: ignore[attr-defined]
    result = container.list_notifications_use_case.execute(
        user_id=g.current_user.id,
        limit=int(request.args.get("limit", 40)),
        offset=int(request.args.get("offset", 0)),
        unread_only=request.args.get("unread_only", "false").lower() == "true",
    )
    return jsonify(result), 200


@notifications_bp.patch("/notifications/<uuid:notification_id>/read")
@require_auth
def mark_notification_read(notification_id: UUID):
    container: Container = notifications_bp.container  # type: ignore[attr-defined]
    result = container.mark_notification_read_use_case.execute(
        user_id=g.current_user.id,
        notification_id=notification_id,
    )
    return jsonify(result), 200


@notifications_bp.post("/notifications/read-all")
@require_auth
def mark_all_notifications_read():
    container: Container = notifications_bp.container  # type: ignore[attr-defined]
    result = container.mark_all_notifications_read_use_case.execute(user_id=g.current_user.id)
    return jsonify(result), 200


@notifications_bp.get("/projects/<uuid:project_id>/chat/poll")
@require_auth
def poll_chat(project_id: UUID):
    container: Container = notifications_bp.container  # type: ignore[attr-defined]
    after_id = request.args.get("after_id")
    result = container.poll_chat_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        after_id=UUID(after_id) if after_id else None,
    )
    return jsonify(result), 200


@notifications_bp.post("/projects/<uuid:project_id>/chat/read")
@require_auth
def mark_chat_read(project_id: UUID):
    try:
        data = MarkChatReadSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = notifications_bp.container  # type: ignore[attr-defined]
    result = container.mark_chat_read_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        message_id=data.get("message_id"),
    )
    return jsonify(result), 200


@notifications_bp.post("/projects/<uuid:project_id>/chat/presence")
@require_auth
def chat_presence_heartbeat(project_id: UUID):
    try:
        PresenceHeartbeatSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = notifications_bp.container  # type: ignore[attr-defined]
    result = container.chat_presence_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
    )
    return jsonify(result), 200


@notifications_bp.get("/projects/<uuid:project_id>/chat/stream")
@require_auth
def chat_stream(project_id: UUID):
    """SSE — novas mensagens e presença (fallback auth via query token)."""
    container: Container = notifications_bp.container  # type: ignore[attr-defined]
    after_id = request.args.get("after_id")

    def generate():
        last_id = UUID(after_id) if after_id else None
        idle = 0
        while idle < 120:
            result = container.poll_chat_use_case.execute(
                actor_id=g.current_user.id,
                project_id=project_id,
                after_id=last_id,
            )
            if result.get("messages"):
                for msg in result["messages"]:
                    if last_id is None or msg["id"] != str(last_id):
                        last_id = UUID(msg["id"])
                yield f"data: {json.dumps(result)}\n\n"
                idle = 0
            else:
                idle += 1
                yield f": keepalive\n\n"
            time.sleep(2)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
