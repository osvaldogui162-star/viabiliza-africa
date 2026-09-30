from uuid import UUID

from flask import Blueprint, g, jsonify, request
from marshmallow import ValidationError as MarshmallowValidationError

from app.di.container import Container
from app.presentation.decorators.rbac import require_auth
from app.presentation.schemas.subscription_schemas import (
    CheckoutQuerySchema,
    InitiateAppyPayPaymentSchema,
    SubscribeSchema,
)

subscriptions_bp = Blueprint("subscriptions", __name__, url_prefix="/api/v1")


@subscriptions_bp.get("/plans")
def list_public_plans():
    container: Container = subscriptions_bp.container  # type: ignore[attr-defined]
    result = container.list_public_plans_use_case.execute()
    return jsonify(result), 200


@subscriptions_bp.get("/plans/checkout-preview")
def checkout_preview():
    try:
        data = CheckoutQuerySchema().load(request.args.to_dict())
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = subscriptions_bp.container  # type: ignore[attr-defined]
    result = container.prepare_checkout_use_case.execute(
        plan_code=data["plan_code"],
        billing_cycle=data.get("billing_cycle", "monthly"),
        currency=data.get("currency", "USD"),
    )
    return jsonify(result), 200


@subscriptions_bp.get("/me/subscription/checkout")
@require_auth
def prepare_checkout():
    try:
        data = CheckoutQuerySchema().load(request.args.to_dict())
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = subscriptions_bp.container  # type: ignore[attr-defined]
    result = container.prepare_checkout_use_case.execute(
        plan_code=data["plan_code"],
        billing_cycle=data.get("billing_cycle", "monthly"),
        currency=data.get("currency", "USD"),
    )
    return jsonify(result), 200


@subscriptions_bp.get("/me/subscription")
@require_auth
def get_my_subscription():
    container: Container = subscriptions_bp.container  # type: ignore[attr-defined]
    result = container.get_my_subscription_use_case.execute(user_id=g.current_user.id)
    return jsonify(result), 200


@subscriptions_bp.post("/me/subscription/payments/appypay")
@require_auth
def initiate_appypay_payment():
    """Inicia pagamento AppyPay (Multicaixa Express ou Referência)."""
    try:
        data = InitiateAppyPayPaymentSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = subscriptions_bp.container  # type: ignore[attr-defined]
    result = container.initiate_appypay_payment_use_case.execute(
        user_id=g.current_user.id,
        plan_code=data["plan_code"],
        billing_cycle=data.get("billing_cycle", "monthly"),
        payment_method=data["payment_method"],
        phone_number=data.get("phone_number"),
    )
    return jsonify(result), 200


@subscriptions_bp.get("/me/subscription/payments/<uuid:payment_id>")
@require_auth
def poll_appypay_payment(payment_id: UUID):
    container: Container = subscriptions_bp.container  # type: ignore[attr-defined]
    result = container.poll_appypay_payment_use_case.execute(
        user_id=g.current_user.id,
        payment_id=payment_id,
    )
    return jsonify(result), 200


@subscriptions_bp.post("/me/subscription/payments/<uuid:payment_id>/mock-reference")
@require_auth
def mock_appypay_reference(payment_id: UUID):
    """Sandbox — simula pagamento de referência Multicaixa."""
    container: Container = subscriptions_bp.container  # type: ignore[attr-defined]
    if not container.config.APPYPAY_SANDBOX:
        return jsonify({"error": {"code": "forbidden", "message": "Disponível apenas em sandbox"}}), 403
    result = container.mock_appypay_reference_use_case.execute(
        user_id=g.current_user.id,
        payment_id=payment_id,
    )
    return jsonify(result), 200


@subscriptions_bp.post("/me/subscription")
@require_auth
def subscribe_to_plan():
    """Activar apenas o plano gratuito. Planos pagos exigem pagamento AppyPay."""
    try:
        data = SubscribeSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = subscriptions_bp.container  # type: ignore[attr-defined]
    result = container.subscribe_to_plan_use_case.execute(
        user_id=g.current_user.id,
        plan_code=data["plan_code"],
        billing_cycle=data.get("billing_cycle", "monthly"),
        currency=data.get("currency", "AOA"),
        payment_method=data.get("payment_method"),
    )
    return jsonify(result), 200
