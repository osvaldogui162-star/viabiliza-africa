from datetime import datetime
from uuid import UUID

from flask import Blueprint, g, jsonify, request
from marshmallow import ValidationError as MarshmallowValidationError

from app.application.dto.auth_dto import (
    ApproveUserInput,
    ExtendUserAccessInput,
    UpdateUserInput,
    UpdateUserRoleInput,
)
from app.di.container import Container
from app.domain.enums.user_role import UserRole
from app.presentation.decorators.rbac import require_roles
from app.presentation.schemas.admin_config_schemas import (
    AssignSubscriptionSchema,
    CreateBudgetTemplateSchema,
    CreateScrapingSourceSchema,
    CreateSubscriptionPlanSchema,
    UpdateBudgetTemplateSchema,
    UpdateIntegrationSchema,
    UpdateScrapingSourceSchema,
    UpdateSubscriptionPlanSchema,
    UpdateSubscriptionStatusSchema,
)
from app.presentation.schemas.auth_schemas import (
    ApproveUserSchema,
    ExtendUserAccessSchema,
    UpdateUserRoleSchema,
    UpdateUserSchema,
)
from app.presentation.serializers import to_dict


admin_bp = Blueprint("admin", __name__, url_prefix="/api/v1/admin")


def _client_meta() -> dict:
    return {
        "ip_address": request.headers.get("X-Forwarded-For", request.remote_addr),
        "user_agent": request.headers.get("User-Agent"),
    }


def _parse_pagination() -> tuple[int, int]:
    limit = min(int(request.args.get("limit", 50)), 100)
    offset = max(int(request.args.get("offset", 0)), 0)
    return limit, offset


@admin_bp.get("/users")
@require_roles(UserRole.ADMIN)
def list_users():
    """Listar utilizadores (UC01/UC04)."""
    limit, offset = _parse_pagination()
    role = request.args.get("role")
    is_active_param = request.args.get("is_active")
    is_active = None
    if is_active_param is not None:
        is_active = is_active_param.lower() in ("true", "1", "yes")

    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.list_users_use_case.execute(
        admin_user_id=g.current_user.id,
        role=role,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )
    return jsonify(to_dict(result)), 200


@admin_bp.get("/users/<uuid:user_id>")
@require_roles(UserRole.ADMIN)
def get_user(user_id: UUID):
    """Detalhes de um utilizador."""
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.get_user_use_case.execute(
        admin_user_id=g.current_user.id,
        target_user_id=user_id,
    )
    return jsonify(to_dict(result)), 200


@admin_bp.patch("/users/<uuid:user_id>")
@require_roles(UserRole.ADMIN)
def update_user(user_id: UUID):
    """UC04 — Editar utilizador (perfil, nome, estado)."""
    try:
        data = UpdateUserSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.update_user_use_case.execute(
        UpdateUserInput(
            target_user_id=user_id,
            admin_user_id=g.current_user.id,
            full_name=data.get("full_name"),
            role=data.get("role"),
            bank_code=data.get("bank_code"),
            is_active=data.get("is_active"),
            **_client_meta(),
        )
    )
    return jsonify(to_dict(result)), 200


@admin_bp.post("/users/<uuid:user_id>/approve")
@require_roles(UserRole.ADMIN)
def approve_user(user_id: UUID):
    """Aprovar registo pendente — activar, plano e prazo."""
    try:
        data = ApproveUserSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.approve_user_use_case.execute(
        ApproveUserInput(
            admin_user_id=g.current_user.id,
            target_user_id=user_id,
            role=data.get("role"),
            plan_id=data.get("plan_id"),
            access_days=data.get("access_days"),
            **_client_meta(),
        )
    )
    return jsonify(to_dict(result)), 200


@admin_bp.post("/users/<uuid:user_id>/extend-access")
@require_roles(UserRole.ADMIN)
def extend_user_access(user_id: UUID):
    """Renovar plano e prazo de acesso de um analista."""
    try:
        data = ExtendUserAccessSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.extend_user_access_use_case.execute(
        ExtendUserAccessInput(
            admin_user_id=g.current_user.id,
            target_user_id=user_id,
            plan_id=data["plan_id"],
            access_days=data["access_days"],
            **_client_meta(),
        )
    )
    return jsonify(to_dict(result)), 200


@admin_bp.patch("/users/<uuid:user_id>/role")
@require_roles(UserRole.ADMIN)
def update_user_role(user_id: UUID):
    """UC04 — Atribuir ou revogar perfil de acesso."""
    try:
        data = UpdateUserRoleSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.update_user_role_use_case.execute(
        UpdateUserRoleInput(
            target_user_id=user_id,
            role=data["role"],
            bank_code=data.get("bank_code"),
            admin_user_id=g.current_user.id,
            **_client_meta(),
        )
    )
    return jsonify(to_dict(result)), 200


@admin_bp.get("/access-logs")
@require_roles(UserRole.ADMIN)
def get_access_logs():
    """UC05 — Ver log de acessos."""
    limit, offset = _parse_pagination()
    user_id_param = request.args.get("user_id")
    action = request.args.get("action")
    from_date_param = request.args.get("from_date")
    to_date_param = request.args.get("to_date")

    from_date = datetime.fromisoformat(from_date_param) if from_date_param else None
    to_date = datetime.fromisoformat(to_date_param) if to_date_param else None
    user_id = UUID(user_id_param) if user_id_param else None

    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.get_access_logs_use_case.execute(
        admin_user_id=g.current_user.id,
        user_id=user_id,
        action=action,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )
    return jsonify(to_dict(result)), 200


# ---------------------------------------------------------------------------
# Módulo 7 — Administração e Configuração
# ---------------------------------------------------------------------------


@admin_bp.get("/customers")
@require_roles(UserRole.ADMIN)
def list_admin_customers():
    limit, offset = _parse_pagination()
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.list_admin_customers_use_case.execute(
        actor_id=g.current_user.id, limit=limit, offset=offset
    )
    return jsonify(result), 200


@admin_bp.post("/plans/sync-catalog")
@require_roles(UserRole.ADMIN)
def sync_plans_catalog():
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.sync_subscription_plans_use_case.execute(actor_id=g.current_user.id)
    return jsonify(result), 200


@admin_bp.get("/commercial/promotion")
@require_roles(UserRole.ADMIN)
def get_pricing_promotion():
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.manage_pricing_promotion_use_case.get_status(actor_id=g.current_user.id)
    return jsonify(result), 200


@admin_bp.get("/commercial/promotion/overview")
@require_roles(UserRole.ADMIN)
def get_pricing_promotion_overview():
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.manage_pricing_promotion_use_case.get_overview(actor_id=g.current_user.id)
    return jsonify(result), 200


@admin_bp.post("/commercial/promotion/activate")
@require_roles(UserRole.ADMIN)
def activate_pricing_promotion():
    body = request.get_json(silent=True) or {}
    duration = int(body.get("duration_months") or 3)
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.manage_pricing_promotion_use_case.activate(
        actor_id=g.current_user.id,
        duration_months=duration,
    )
    return jsonify(result), 200


@admin_bp.post("/commercial/promotion/deactivate")
@require_roles(UserRole.ADMIN)
def deactivate_pricing_promotion():
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.manage_pricing_promotion_use_case.deactivate(actor_id=g.current_user.id)
    return jsonify(result), 200


@admin_bp.get("/billing/overview")
@require_roles(UserRole.ADMIN)
def billing_overview():
    """Resumo financeiro: subscrições, pagamentos, utilizadores."""
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.get_billing_overview_use_case.execute(actor_id=g.current_user.id)
    scraping = container.list_scraping_sources_admin_use_case.execute(actor_id=g.current_user.id)
    integrations = container.list_integrations_use_case.execute(actor_id=g.current_user.id)
    templates = container.list_budget_templates_use_case.execute(actor_id=g.current_user.id)
    plans = container.list_subscription_plans_use_case.execute(actor_id=g.current_user.id)
    audit = container.get_global_audit_trail_use_case.execute(
        actor_id=g.current_user.id, limit=1, offset=0
    )
    result["system"] = {
        "scraping_sources": scraping["total"],
        "integrations": integrations["total"],
        "budget_templates": templates["total"],
        "subscription_plans": plans["total"],
        "audit_records": audit["total"],
    }
    return jsonify(result), 200


@admin_bp.get("/payments")
@require_roles(UserRole.ADMIN)
def list_admin_payments():
    limit, offset = _parse_pagination()
    status = request.args.get("status")
    user_id_param = request.args.get("user_id")
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.list_admin_payments_use_case.execute(
        actor_id=g.current_user.id,
        status=status,
        user_id=UUID(user_id_param) if user_id_param else None,
        limit=limit,
        offset=offset,
    )
    return jsonify(result), 200


@admin_bp.get("/settings/overview")
@require_roles(UserRole.ADMIN)
def settings_overview():
    """Resumo de todas as configurações do sistema."""
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    scraping = container.list_scraping_sources_admin_use_case.execute(actor_id=g.current_user.id)
    integrations = container.list_integrations_use_case.execute(actor_id=g.current_user.id)
    templates = container.list_budget_templates_use_case.execute(actor_id=g.current_user.id)
    plans = container.list_subscription_plans_use_case.execute(actor_id=g.current_user.id)
    return jsonify(
        {
            "scraping_sources": scraping["total"],
            "integrations": integrations["total"],
            "budget_templates": templates["total"],
            "subscription_plans": plans["total"],
        }
    ), 200


@admin_bp.get("/scraping-sources")
@require_roles(UserRole.ADMIN)
def list_scraping_sources_admin():
    """UC35 — Listar fontes de scraping."""
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.list_scraping_sources_admin_use_case.execute(actor_id=g.current_user.id)
    return jsonify(result), 200


@admin_bp.post("/scraping-sources")
@require_roles(UserRole.ADMIN)
def create_scraping_source():
    """UC35 — Adicionar fonte de scraping."""
    try:
        data = CreateScrapingSourceSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.create_scraping_source_use_case.execute(
        actor_id=g.current_user.id, **data
    )
    return jsonify(result), 201


@admin_bp.patch("/scraping-sources/<uuid:source_id>")
@require_roles(UserRole.ADMIN)
def update_scraping_source(source_id: UUID):
    """UC35 — Actualizar fonte de scraping."""
    try:
        data = UpdateScrapingSourceSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.update_scraping_source_use_case.execute(
        actor_id=g.current_user.id, source_id=source_id, **data
    )
    return jsonify(result), 200


@admin_bp.delete("/scraping-sources/<uuid:source_id>")
@require_roles(UserRole.ADMIN)
def delete_scraping_source(source_id: UUID):
    """UC35 — Remover fonte de scraping."""
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.delete_scraping_source_use_case.execute(
        actor_id=g.current_user.id, source_id=source_id
    )
    return jsonify(result), 200


@admin_bp.get("/integrations")
@require_roles(UserRole.ADMIN)
def list_integrations():
    """UC36 — Listar integrações."""
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.list_integrations_use_case.execute(actor_id=g.current_user.id)
    return jsonify(result), 200


@admin_bp.get("/integrations/<integration_key>")
@require_roles(UserRole.ADMIN)
def get_integration(integration_key: str):
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.get_integration_use_case.execute(
        actor_id=g.current_user.id, integration_key=integration_key
    )
    return jsonify(result), 200


@admin_bp.patch("/integrations/<integration_key>")
@require_roles(UserRole.ADMIN)
def update_integration(integration_key: str):
    """UC36 — Configurar credenciais de integração."""
    try:
        data = UpdateIntegrationSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.update_integration_use_case.execute(
        actor_id=g.current_user.id,
        integration_key=integration_key,
        settings=data["settings"],
        is_active=data.get("is_active", True),
    )
    return jsonify(result), 200


@admin_bp.post("/integrations/<integration_key>/test")
@require_roles(UserRole.ADMIN)
def test_integration(integration_key: str):
    """UC36 — Testar ligação à API."""
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.test_integration_use_case.execute(
        actor_id=g.current_user.id, integration_key=integration_key
    )
    return jsonify(result), 200


@admin_bp.get("/budget-templates")
@require_roles(UserRole.ADMIN)
def list_budget_templates():
    """UC37 — Listar templates."""
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.list_budget_templates_use_case.execute(actor_id=g.current_user.id)
    return jsonify(result), 200


@admin_bp.post("/budget-templates")
@require_roles(UserRole.ADMIN)
def create_budget_template():
    """UC37 — Criar template."""
    try:
        data = CreateBudgetTemplateSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.create_budget_template_use_case.execute(
        actor_id=g.current_user.id, **data
    )
    return jsonify(result), 201


@admin_bp.patch("/budget-templates/<uuid:template_id>")
@require_roles(UserRole.ADMIN)
def update_budget_template(template_id: UUID):
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    try:
        data = UpdateBudgetTemplateSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    result = container.update_budget_template_use_case.execute(
        actor_id=g.current_user.id, template_id=template_id, **data
    )
    return jsonify(result), 200


@admin_bp.post("/budget-templates/<uuid:template_id>/set-default")
@require_roles(UserRole.ADMIN)
def set_default_budget_template(template_id: UUID):
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.set_default_budget_template_use_case.execute(
        actor_id=g.current_user.id, template_id=template_id
    )
    return jsonify(result), 200


@admin_bp.delete("/budget-templates/<uuid:template_id>")
@require_roles(UserRole.ADMIN)
def delete_budget_template(template_id: UUID):
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.delete_budget_template_use_case.execute(
        actor_id=g.current_user.id, template_id=template_id
    )
    return jsonify(result), 200


@admin_bp.get("/audit-trail")
@require_roles(UserRole.ADMIN)
def get_global_audit_trail():
    """UC38 — Auditoria completa (todos os projectos)."""
    limit, offset = _parse_pagination()
    project_id_param = request.args.get("project_id")
    actor_param = request.args.get("actor_id")
    entity_type = request.args.get("entity_type")
    action = request.args.get("action")
    from_date_param = request.args.get("from_date")
    to_date_param = request.args.get("to_date")

    from_date = datetime.fromisoformat(from_date_param) if from_date_param else None
    to_date = datetime.fromisoformat(to_date_param) if to_date_param else None

    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.get_global_audit_trail_use_case.execute(
        actor_id=g.current_user.id,
        project_id=UUID(project_id_param) if project_id_param else None,
        filter_actor_id=UUID(actor_param) if actor_param else None,
        entity_type=entity_type,
        action=action,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )
    return jsonify(to_dict(result)), 200


@admin_bp.get("/plans")
@require_roles(UserRole.ADMIN)
def list_subscription_plans():
    """UC39 — Listar planos."""
    active_only = request.args.get("active_only", "false").lower() in ("true", "1")
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.list_subscription_plans_use_case.execute(
        actor_id=g.current_user.id, active_only=active_only
    )
    return jsonify(result), 200


@admin_bp.post("/plans")
@require_roles(UserRole.ADMIN)
def create_subscription_plan():
    try:
        data = CreateSubscriptionPlanSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.create_subscription_plan_use_case.execute(
        actor_id=g.current_user.id, **data
    )
    return jsonify(result), 201


@admin_bp.patch("/plans/<uuid:plan_id>")
@require_roles(UserRole.ADMIN)
def update_subscription_plan(plan_id: UUID):
    try:
        data = UpdateSubscriptionPlanSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.update_subscription_plan_use_case.execute(
        actor_id=g.current_user.id, plan_id=plan_id, **data
    )
    return jsonify(result), 200


@admin_bp.delete("/plans/<uuid:plan_id>")
@require_roles(UserRole.ADMIN)
def delete_subscription_plan(plan_id: UUID):
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.delete_subscription_plan_use_case.execute(
        actor_id=g.current_user.id, plan_id=plan_id
    )
    return jsonify(result), 200


@admin_bp.get("/subscriptions")
@require_roles(UserRole.ADMIN)
def list_user_subscriptions():
    limit, offset = _parse_pagination()
    user_id_param = request.args.get("user_id")
    status = request.args.get("status")
    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.list_user_subscriptions_use_case.execute(
        actor_id=g.current_user.id,
        user_id=UUID(user_id_param) if user_id_param else None,
        status=status,
        limit=limit,
        offset=offset,
    )
    return jsonify(to_dict(result)), 200


@admin_bp.post("/subscriptions")
@require_roles(UserRole.ADMIN)
def assign_user_subscription():
    try:
        data = AssignSubscriptionSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.assign_user_subscription_use_case.execute(
        actor_id=g.current_user.id,
        user_id=data["user_id"],
        plan_id=data["plan_id"],
        status=data.get("status", "active"),
        ends_at=data.get("ends_at"),
    )
    return jsonify(to_dict(result)), 201


@admin_bp.patch("/subscriptions/<uuid:subscription_id>")
@require_roles(UserRole.ADMIN)
def update_user_subscription(subscription_id: UUID):
    try:
        data = UpdateSubscriptionStatusSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = admin_bp.container  # type: ignore[attr-defined]
    result = container.update_user_subscription_status_use_case.execute(
        actor_id=g.current_user.id,
        subscription_id=subscription_id,
        status=data["status"],
    )
    return jsonify(to_dict(result)), 200
