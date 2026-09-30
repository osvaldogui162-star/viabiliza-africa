from uuid import UUID

from flask import Blueprint, g, jsonify, request
from marshmallow import Schema, ValidationError as MarshmallowValidationError, fields, validate

from app.di.container import Container
from app.domain.enums.project_capability import ProjectCapability
from app.domain.enums.share_permission import SharePermission
from app.presentation.decorators.rbac import require_auth, require_roles
from app.domain.enums.user_role import UserRole


office_bp = Blueprint("office", __name__)


class OfficeMemberSchema(Schema):
    email = fields.Email(required=True)
    full_name = fields.String(required=True, validate=validate.Length(min=2, max=200))
    job_title = fields.String(load_default="Colaborador", validate=validate.Length(max=120))
    notes = fields.String(load_default=None, allow_none=True)


class UpdateOfficeMemberSchema(Schema):
    full_name = fields.String(validate=validate.Length(min=2, max=200))
    job_title = fields.String(validate=validate.Length(max=120))
    notes = fields.String(allow_none=True)


class ProjectAssignmentSchema(Schema):
    project_id = fields.UUID(required=True)
    permission = fields.String(
        load_default="collaborate",
        validate=validate.OneOf(SharePermission.values()),
    )
    capabilities = fields.Dict(keys=fields.String(), values=fields.Boolean(), load_default=None)


class AssignProjectsSchema(Schema):
    assignments = fields.List(fields.Nested(ProjectAssignmentSchema), required=True)
    project_ids = fields.List(fields.UUID(), load_default=None)
    permission = fields.String(
        load_default="collaborate",
        validate=validate.OneOf(SharePermission.values()),
    )
    capabilities = fields.Dict(keys=fields.String(), values=fields.Boolean(), load_default=None)


def _owner_id_param() -> UUID | None:
    raw = request.args.get("owner_id")
    return UUID(raw) if raw else None


@office_bp.get("/api/v1/office/dashboard")
@require_auth
def office_dashboard():
    container: Container = office_bp.container  # type: ignore[attr-defined]
    result = container.get_office_dashboard_use_case.execute(
        actor_id=g.current_user.id,
        owner_id=_owner_id_param(),
    )
    return jsonify(result), 200


@office_bp.get("/api/v1/office/members")
@require_auth
def list_office_members():
    container: Container = office_bp.container  # type: ignore[attr-defined]
    result = container.list_office_members_use_case.execute(
        actor_id=g.current_user.id,
        owner_id=_owner_id_param(),
    )
    return jsonify(result), 200


@office_bp.post("/api/v1/office/members")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def create_office_member():
    try:
        data = OfficeMemberSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400
    container: Container = office_bp.container  # type: ignore[attr-defined]
    result = container.create_office_member_use_case.execute(
        actor_id=g.current_user.id,
        owner_id=_owner_id_param(),
        email=data["email"],
        full_name=data["full_name"],
        job_title=data.get("job_title", "Colaborador"),
        notes=data.get("notes"),
    )
    return jsonify(result), 201


@office_bp.patch("/api/v1/office/members/<uuid:member_id>")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def update_office_member(member_id: UUID):
    try:
        data = UpdateOfficeMemberSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400
    container: Container = office_bp.container  # type: ignore[attr-defined]
    result = container.update_office_member_use_case.execute(
        actor_id=g.current_user.id,
        member_id=member_id,
        full_name=data.get("full_name"),
        job_title=data.get("job_title"),
        notes=data.get("notes"),
    )
    return jsonify(result), 200


@office_bp.delete("/api/v1/office/members/<uuid:member_id>")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def archive_office_member(member_id: UUID):
    container: Container = office_bp.container  # type: ignore[attr-defined]
    result = container.archive_office_member_use_case.execute(
        actor_id=g.current_user.id,
        member_id=member_id,
    )
    return jsonify(result), 200


@office_bp.post("/api/v1/office/members/<uuid:member_id>/assign-projects")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def assign_office_projects(member_id: UUID):
    try:
        data = AssignProjectsSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400
    container: Container = office_bp.container  # type: ignore[attr-defined]
    def _clean_caps(raw):
        if not raw:
            return None
        return {k: v for k, v in raw.items() if k in ProjectCapability.keys()}

    assignments = None
    if data.get("assignments"):
        assignments = []
        for row in data["assignments"]:
            assignments.append(
                {
                    "project_id": row["project_id"],
                    "permission": row.get("permission", "collaborate"),
                    "capabilities": _clean_caps(row.get("capabilities")),
                }
            )
    caps = _clean_caps(data.get("capabilities"))
    result = container.assign_office_member_projects_use_case.execute(
        actor_id=g.current_user.id,
        member_id=member_id,
        project_ids=data.get("project_ids"),
        permission=data.get("permission", "collaborate"),
        capabilities=caps,
        assignments=assignments,
    )
    return jsonify(result), 200


@office_bp.get("/api/v1/office/members/<uuid:member_id>/access")
@require_auth
def list_member_access(member_id: UUID):
    container: Container = office_bp.container  # type: ignore[attr-defined]
    result = container.list_office_member_access_use_case.execute(
        actor_id=g.current_user.id,
        member_id=member_id,
    )
    return jsonify(result), 200


@office_bp.get("/api/v1/admin/offices")
@require_roles(UserRole.ADMIN)
def admin_list_offices():
    container: Container = office_bp.container  # type: ignore[attr-defined]
    result = container.admin_list_offices_use_case.execute(actor_id=g.current_user.id)
    return jsonify(result), 200
