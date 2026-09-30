from io import BytesIO
from uuid import UUID

from flask import Blueprint, g, jsonify, request, send_file
from marshmallow import ValidationError as MarshmallowValidationError

from app.di.container import Container
from app.domain.enums.user_role import UserRole
from app.presentation.decorators.rbac import require_auth, require_roles
from app.presentation.schemas.report_schemas import (
    GenerateReportSchema,
    SendReportEmailSchema,
    ShareReportWhatsAppSchema,
    SubmitBankReportSchema,
)
from app.presentation.serializers import to_dict


reports_bp = Blueprint("reports", __name__)


def _validation_error(exc: MarshmallowValidationError):
    return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400


@reports_bp.get("/api/v1/projects/<uuid:project_id>/reports")
@require_auth
def list_reports(project_id: UUID):
    container: Container = reports_bp.container  # type: ignore[attr-defined]
    result = container.list_reports_use_case.execute(actor_id=g.current_user.id, project_id=project_id)
    return jsonify(result), 200


@reports_bp.post("/api/v1/projects/<uuid:project_id>/reports")
@require_auth
def generate_report(project_id: UUID):
    """UC28/UC29/UC30 — Gerar relatório PDF."""
    try:
        data = GenerateReportSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = reports_bp.container  # type: ignore[attr-defined]
    result = container.generate_report_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        report_type=data["report_type"],
        language=data["language"],
        currency=data["currency"],
        print_optimized=data.get("print_optimized", False),
    )
    return jsonify(to_dict(result)), 201


@reports_bp.get("/api/v1/projects/<uuid:project_id>/reports/<uuid:report_id>")
@require_auth
def get_report(project_id: UUID, report_id: UUID):
    container: Container = reports_bp.container  # type: ignore[attr-defined]
    result = container.get_report_use_case.execute(
        actor_id=g.current_user.id, project_id=project_id, report_id=report_id
    )
    return jsonify(to_dict(result)), 200


@reports_bp.get("/api/v1/projects/<uuid:project_id>/reports/<uuid:report_id>/download")
@require_auth
def download_report(project_id: UUID, report_id: UUID):
    container: Container = reports_bp.container  # type: ignore[attr-defined]
    content, filename, _ = container.download_report_use_case.execute(
        actor_id=g.current_user.id, project_id=project_id, report_id=report_id, inline=False
    )
    return send_file(
        BytesIO(content),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@reports_bp.get("/api/v1/projects/<uuid:project_id>/reports/<uuid:report_id>/print")
@require_auth
def print_report(project_id: UUID, report_id: UUID):
    """UC06 — Impressão com registo em auditoria (inline PDF)."""
    container: Container = reports_bp.container  # type: ignore[attr-defined]
    content, filename = container.print_report_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        report_id=report_id,
    )
    return send_file(
        BytesIO(content),
        mimetype="application/pdf",
        as_attachment=False,
        download_name=filename,
    )


@reports_bp.post("/api/v1/projects/<uuid:project_id>/reports/<uuid:report_id>/send-email")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def send_report_email(project_id: UUID, report_id: UUID):
    """UC31 — Enviar relatório por email."""
    try:
        data = SendReportEmailSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = reports_bp.container  # type: ignore[attr-defined]
    result = container.send_report_email_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        report_id=report_id,
        to_email=data["to_email"],
        subject=data.get("subject"),
        message=data.get("message"),
    )
    return jsonify(result), 200


@reports_bp.post("/api/v1/projects/<uuid:project_id>/reports/<uuid:report_id>/share-whatsapp")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def share_whatsapp(project_id: UUID, report_id: UUID):
    """UC32 — Partilhar por WhatsApp (link 7 dias)."""
    try:
        data = ShareReportWhatsAppSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = reports_bp.container  # type: ignore[attr-defined]
    result = container.share_report_whatsapp_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        report_id=report_id,
        phone=data.get("phone"),
    )
    return jsonify(result), 200


@reports_bp.post("/api/v1/projects/<uuid:project_id>/reports/<uuid:report_id>/submit-bank")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def submit_to_bank(project_id: UUID, report_id: UUID):
    """UC34 — Enviar para banco via API."""
    try:
        data = SubmitBankReportSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = reports_bp.container  # type: ignore[attr-defined]
    result = container.submit_report_to_bank_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        report_id=report_id,
        bank_code=data["bank_code"],
    )
    return jsonify(to_dict(result)), 200


@reports_bp.get("/api/v1/reports/share/<token>")
def download_shared_report(token: str):
    """Download público via link temporário (UC32)."""
    container: Container = reports_bp.container  # type: ignore[attr-defined]
    content, filename = container.get_shared_report_use_case.execute(token=token)
    return send_file(
        BytesIO(content),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )
