from uuid import UUID

from flask import Blueprint, g, jsonify, request
from marshmallow import ValidationError as MarshmallowValidationError

from app.di.container import Container
from app.presentation.decorators.rbac import require_auth
from app.domain.catalog.portal_bank_codes import portal_bank_catalog
from app.presentation.schemas.financier_schemas import (
    CreateProjectFinancingSchema,
    DecideProjectFinancingSchema,
)


financier_bp = Blueprint("financier", __name__)


def _validation_error(exc: MarshmallowValidationError):
    return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400


@financier_bp.get("/api/v1/financier/banks")
@require_auth
def list_portal_banks():
    return jsonify({"items": portal_bank_catalog(), "total": len(portal_bank_catalog())}), 200


@financier_bp.get("/api/v1/financier/portfolio")
@require_auth
def list_portfolio():
    container: Container = financier_bp.container  # type: ignore[attr-defined]
    result = container.list_financier_portfolio_use_case.execute(actor_id=g.current_user.id)
    return jsonify(result), 200


@financier_bp.get("/api/v1/financier/pending-approvals")
@require_auth
def list_pending_approvals():
    container: Container = financier_bp.container  # type: ignore[attr-defined]
    result = container.list_financier_pending_approvals_use_case.execute(
        actor_id=g.current_user.id
    )
    return jsonify(result), 200


@financier_bp.patch("/api/v1/financier/financing/<uuid:financing_id>/decision")
@require_auth
def decide_project_financing(financing_id: UUID):
    try:
        data = DecideProjectFinancingSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    from decimal import Decimal

    container: Container = financier_bp.container  # type: ignore[attr-defined]
    result = container.decide_project_financing_use_case.execute(
        actor_id=g.current_user.id,
        financing_id=financing_id,
        decision=data["decision"],
        approved_amount=(
            Decimal(str(data["approved_amount"])) if data.get("approved_amount") is not None else None
        ),
        disbursed_amount=(
            Decimal(str(data["disbursed_amount"])) if data.get("disbursed_amount") is not None else None
        ),
        interest_rate_pct=(
            Decimal(str(data["interest_rate_pct"]))
            if data.get("interest_rate_pct") is not None
            else None
        ),
        term_months=data.get("term_months"),
        notes=data.get("notes"),
    )
    return jsonify(result), 200


@financier_bp.get("/api/v1/financier/dashboard")
@require_auth
def get_dashboard():
    container: Container = financier_bp.container  # type: ignore[attr-defined]
    result = container.get_financier_dashboard_use_case.execute(actor_id=g.current_user.id)
    return jsonify(result), 200


@financier_bp.get("/api/v1/financier/alerts")
@require_auth
def list_alerts():
    container: Container = financier_bp.container  # type: ignore[attr-defined]
    result = container.list_financier_alerts_use_case.execute(actor_id=g.current_user.id)
    return jsonify(result), 200


@financier_bp.get("/api/v1/financier/disbursements")
@require_auth
def list_disbursements():
    container: Container = financier_bp.container  # type: ignore[attr-defined]
    result = container.list_financier_disbursements_use_case.execute(actor_id=g.current_user.id)
    return jsonify(result), 200


@financier_bp.get("/api/v1/financier/documents")
@require_auth
def list_documents():
    container: Container = financier_bp.container  # type: ignore[attr-defined]
    result = container.list_financier_documents_use_case.execute(actor_id=g.current_user.id)
    return jsonify(result), 200


@financier_bp.get("/api/v1/financier/activity")
@require_auth
def list_activity():
    container: Container = financier_bp.container  # type: ignore[attr-defined]
    limit = min(int(request.args.get("limit", 50)), 100)
    result = container.list_financier_activity_use_case.execute(
        actor_id=g.current_user.id, limit=limit
    )
    return jsonify(result), 200


@financier_bp.get("/api/v1/financier/reports/portfolio")
@require_auth
def export_portfolio_report():
    container: Container = financier_bp.container  # type: ignore[attr-defined]
    result = container.export_financier_portfolio_report_use_case.execute(
        actor_id=g.current_user.id
    )
    return jsonify(result), 200


@financier_bp.get("/api/v1/financier/reports/credit")
@require_auth
def export_credit_report():
    container: Container = financier_bp.container  # type: ignore[attr-defined]
    result = container.export_financier_credit_report_use_case.execute(
        actor_id=g.current_user.id
    )
    return jsonify(result), 200


@financier_bp.post("/api/v1/financier/financing/<uuid:financing_id>/disbursements")
@require_auth
def create_disbursement(financing_id: UUID):
    from decimal import Decimal

    data = request.get_json() or {}
    container: Container = financier_bp.container  # type: ignore[attr-defined]
    result = container.create_financing_disbursement_use_case.execute(
        actor_id=g.current_user.id,
        financing_id=financing_id,
        requested_amount=Decimal(str(data.get("requested_amount", "0"))),
        purpose=data.get("purpose"),
    )
    return jsonify(result), 201


@financier_bp.patch("/api/v1/financier/disbursements/<uuid:disbursement_id>")
@require_auth
def update_disbursement(disbursement_id: UUID):
    from decimal import Decimal

    data = request.get_json() or {}
    container: Container = financier_bp.container  # type: ignore[attr-defined]
    approved = data.get("approved_amount")
    result = container.update_financing_disbursement_use_case.execute(
        actor_id=g.current_user.id,
        disbursement_id=disbursement_id,
        status=data["status"],
        approved_amount=Decimal(str(approved)) if approved is not None else None,
        notes=data.get("notes"),
    )
    return jsonify(result), 200


@financier_bp.post("/api/v1/financier/financing/<uuid:financing_id>/documents")
@require_auth
def create_document(financing_id: UUID):
    data = request.get_json() or {}
    container: Container = financier_bp.container  # type: ignore[attr-defined]
    result = container.create_financing_document_use_case.execute(
        actor_id=g.current_user.id,
        financing_id=financing_id,
        doc_type=data.get("doc_type", "other"),
        title=data.get("title", "Documento"),
        file_ref=data.get("file_ref"),
    )
    return jsonify(result), 201


@financier_bp.patch("/api/v1/financier/documents/<uuid:document_id>")
@require_auth
def validate_document(document_id: UUID):
    data = request.get_json() or {}
    container: Container = financier_bp.container  # type: ignore[attr-defined]
    result = container.validate_financing_document_use_case.execute(
        actor_id=g.current_user.id,
        document_id=document_id,
        validation_status=data["validation_status"],
        notes=data.get("notes"),
    )
    return jsonify(result), 200


@financier_bp.get("/api/v1/financier/billing-integrations")
@require_auth
def list_billing_integrations():
    container: Container = financier_bp.container  # type: ignore[attr-defined]
    result = container.list_financier_billing_integrations_use_case.execute(
        actor_id=g.current_user.id
    )
    return jsonify(result), 200


@financier_bp.get("/api/v1/financier/monitoring/<uuid:financing_id>")
@require_auth
def get_monitoring(financing_id: UUID):
    container: Container = financier_bp.container  # type: ignore[attr-defined]
    result = container.get_financier_monitoring_use_case.execute(
        actor_id=g.current_user.id,
        financing_id=financing_id,
    )
    return jsonify(result), 200


@financier_bp.get("/api/v1/projects/<uuid:project_id>/financing")
@require_auth
def list_project_financing(project_id: UUID):
    container: Container = financier_bp.container  # type: ignore[attr-defined]
    result = container.list_project_financings_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
    )
    return jsonify(result), 200


@financier_bp.post("/api/v1/projects/<uuid:project_id>/financing")
@require_auth
def create_project_financing(project_id: UUID):
    try:
        data = CreateProjectFinancingSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    from decimal import Decimal

    container: Container = financier_bp.container  # type: ignore[attr-defined]
    result = container.create_project_financing_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        bank_code=data["bank_code"],
        decision=data["decision"],
        approved_amount=Decimal(str(data["approved_amount"])),
        currency=data["currency"],
        disbursed_amount=(
            Decimal(str(data["disbursed_amount"])) if data.get("disbursed_amount") is not None else None
        ),
        interest_rate_pct=(
            Decimal(str(data["interest_rate_pct"]))
            if data.get("interest_rate_pct") is not None
            else None
        ),
        term_months=data.get("term_months"),
        submission_id=data.get("submission_id"),
        notes=data.get("notes"),
    )
    return jsonify(result), 201
