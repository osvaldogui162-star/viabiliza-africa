from uuid import UUID

from flask import Blueprint, Response, g, jsonify, request
from marshmallow import Schema, ValidationError as MarshmallowValidationError, fields

from app.di.container import Container
from app.presentation.decorators.rbac import require_auth

erp_billing_bp = Blueprint("erp_billing", __name__)


class SaveErpBillingSchema(Schema):
    provider_code = fields.String(required=True)
    config = fields.Dict(keys=fields.String(), values=fields.Raw(), load_default=dict)
    auto_fiscal_on_payment = fields.Boolean(load_default=True)


class TestErpBillingSchema(Schema):
    provider_code = fields.String(load_default=None)
    config = fields.Dict(keys=fields.String(), values=fields.Raw(), load_default=None)


@erp_billing_bp.get("/api/v1/erp-billing/providers")
def list_erp_providers():
    container: Container = erp_billing_bp.container  # type: ignore[attr-defined]
    return jsonify(container.list_erp_billing_providers_use_case.execute()), 200


@erp_billing_bp.get("/api/v1/me/erp-billing")
@require_auth
def get_my_erp_billing():
    container: Container = erp_billing_bp.container  # type: ignore[attr-defined]
    result = container.get_account_erp_billing_use_case.execute(user=g.current_user)
    return jsonify(result), 200


@erp_billing_bp.put("/api/v1/me/erp-billing")
@require_auth
def save_my_erp_billing():
    try:
        data = SaveErpBillingSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400
    container: Container = erp_billing_bp.container  # type: ignore[attr-defined]
    result = container.save_account_erp_billing_use_case.execute(
        user=g.current_user,
        provider_code=data["provider_code"],
        config=data.get("config") or {},
        auto_fiscal_on_payment=data.get("auto_fiscal_on_payment", True),
    )
    return jsonify(result), 200


@erp_billing_bp.post("/api/v1/me/erp-billing/test")
@require_auth
def test_my_erp_billing():
    try:
        data = TestErpBillingSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400
    container: Container = erp_billing_bp.container  # type: ignore[attr-defined]
    result = container.test_account_erp_billing_use_case.execute(
        user=g.current_user,
        provider_code=data.get("provider_code"),
        config=data.get("config"),
    )
    return jsonify(result), 200


@erp_billing_bp.get("/api/v1/me/erp-billing/fiscal-documents/<uuid:document_id>/agt-export")
@require_auth
def download_agt_export(document_id: UUID):
    container: Container = erp_billing_bp.container  # type: ignore[attr-defined]
    result = container.get_subscription_fiscal_export_use_case.execute(
        user=g.current_user,
        document_id=document_id,
    )
    return Response(
        result["agt_export_xml"],
        mimetype="application/xml",
        headers={
            "Content-Disposition": f'attachment; filename="{result["filename"]}"',
        },
    )
