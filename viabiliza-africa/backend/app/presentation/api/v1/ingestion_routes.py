from decimal import Decimal
from uuid import UUID

from flask import Blueprint, g, jsonify, request
from marshmallow import ValidationError as MarshmallowValidationError

from app.di.container import Container
from app.domain.enums.user_role import UserRole
from app.presentation.decorators.rbac import require_auth, require_roles
from app.presentation.schemas.ingestion_schemas import (
    CreateCostItemSchema,
    ExecuteScrapingSchema,
    GenerateBudgetSchema,
    GenerateProformaSchema,
    RunAutoIngestionSchema,
    SelectSupplierSchema,
    UpdateCostItemSchema,
)
from app.presentation.serializers import to_dict


ingestion_bp = Blueprint("ingestion", __name__, url_prefix="/api/v1/projects")


def _ip_address() -> str | None:
    return request.headers.get("X-Forwarded-For", request.remote_addr)


def _validation_error(exc: MarshmallowValidationError):
    return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400


@ingestion_bp.get("/scraping/sources")
@require_auth
def list_scraping_sources():
    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    return jsonify(container.list_scraping_sources_use_case.execute()), 200


@ingestion_bp.get("/<uuid:project_id>/ingestion/auto/preview")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def preview_auto_ingestion(project_id: UUID):
    """Pré-visualiza itens do catálogo setorial para ingestão automática."""
    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.preview_auto_ingestion_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
    )
    return jsonify(result), 200


@ingestion_bp.post("/<uuid:project_id>/ingestion/auto/run")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def run_auto_ingestion(project_id: UUID):
    """
    Pipeline: catálogo setorial → preços reais → cost items → orçamento → proforma.
    Devolve documento de transparência (preço + fonte por item).
    """
    try:
        data = RunAutoIngestionSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.run_auto_ingestion_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        sources=data.get("sources"),
        replace_existing=bool(data.get("replace_existing")),
        generate_proforma=bool(data.get("generate_proforma", True)),
        item_overrides=data.get("items"),
        ip_address=_ip_address(),
    )
    return jsonify(to_dict(result)), 201


@ingestion_bp.get("/<uuid:project_id>/cost-items")
@require_auth
def list_cost_items(project_id: UUID):
    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.list_cost_items_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        item_type=request.args.get("item_type"),
    )
    return jsonify(to_dict(result)), 200


@ingestion_bp.post("/<uuid:project_id>/cost-items")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def create_cost_item(project_id: UUID):
    """UC12 — Importar manualmente."""
    try:
        data = CreateCostItemSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.create_cost_item_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        item_type=data["item_type"],
        category=data["category"],
        description=data["description"],
        quantity=Decimal(str(data["quantity"])),
        unit=data.get("unit", "un"),
        unit_price=Decimal(str(data["unit_price"])),
        supplier_nif=data.get("supplier_nif"),
        supplier_name=data.get("supplier_name"),
        ip_address=_ip_address(),
    )
    return jsonify(to_dict(result)), 201


@ingestion_bp.post("/<uuid:project_id>/cost-items/import/excel")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def import_excel(project_id: UUID):
    """UC13 — Importar via Excel."""
    if "file" not in request.files:
        return jsonify({"error": {"code": "validation_error", "message": "Ficheiro em falta"}}), 400
    file = request.files["file"]
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xls")):
        return jsonify({"error": {"code": "validation_error", "message": "Formato deve ser .xlsx"}}), 400

    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.import_cost_items_excel_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        file_bytes=file.read(),
        ip_address=_ip_address(),
    )
    return jsonify(to_dict(result)), 201


@ingestion_bp.patch("/<uuid:project_id>/cost-items/<uuid:item_id>")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def update_cost_item(project_id: UUID, item_id: UUID):
    """Actualizar item de custo manualmente (re-hash SHA-256)."""
    try:
        data = UpdateCostItemSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.update_cost_item_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        item_id=item_id,
        category=data.get("category"),
        description=data.get("description"),
        quantity=Decimal(str(data["quantity"])) if data.get("quantity") is not None else None,
        unit=data.get("unit"),
        unit_price=Decimal(str(data["unit_price"])) if data.get("unit_price") is not None else None,
        ip_address=_ip_address(),
    )
    return jsonify(to_dict(result)), 200


@ingestion_bp.delete("/<uuid:project_id>/cost-items/<uuid:item_id>")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def delete_cost_item(project_id: UUID, item_id: UUID):
    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.delete_cost_item_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        item_id=item_id,
        ip_address=_ip_address(),
    )
    return jsonify(result), 200


@ingestion_bp.post("/<uuid:project_id>/scraping/jobs")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def execute_scraping(project_id: UUID):
    """UC14 — Executar scraping."""
    try:
        data = ExecuteScrapingSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.execute_scraping_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        search_query=data["search_query"],
        sources=data.get("sources"),
        ip_address=_ip_address(),
    )
    return jsonify(to_dict(result)), 201


@ingestion_bp.get("/<uuid:project_id>/scraping/jobs/<uuid:job_id>")
@require_auth
def get_scraping_job(project_id: UUID, job_id: UUID):
    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.get_scraping_job_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        job_id=job_id,
    )
    return jsonify(to_dict(result)), 200


@ingestion_bp.post("/<uuid:project_id>/scraping/results/<uuid:result_id>/select")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def select_supplier(project_id: UUID, result_id: UUID):
    """UC15 — Selecionar fornecedor."""
    try:
        data = SelectSupplierSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.select_supplier_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        result_id=result_id,
        item_type=data.get("item_type", "capex"),
        category=data.get("category", "Equipamento"),
        quantity=Decimal(str(data.get("quantity", "1"))),
        ip_address=_ip_address(),
    )
    return jsonify(to_dict(result)), 201


@ingestion_bp.get("/<uuid:project_id>/budgets")
@require_auth
def list_budgets(project_id: UUID):
    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.list_budgets_use_case.execute(
        actor_id=g.current_user.id, project_id=project_id
    )
    return jsonify(to_dict(result)), 200


@ingestion_bp.post("/<uuid:project_id>/budgets")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def generate_budget(project_id: UUID):
    """UC16 — Gerar orçamento rastreável."""
    try:
        data = GenerateBudgetSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.generate_budget_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        title=data.get("title", "Orçamento Rastreável"),
        ip_address=_ip_address(),
    )
    return jsonify(to_dict(result)), 201


@ingestion_bp.get("/<uuid:project_id>/budgets/<uuid:budget_id>")
@require_auth
def get_budget(project_id: UUID, budget_id: UUID):
    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.get_budget_use_case.execute(
        actor_id=g.current_user.id, project_id=project_id, budget_id=budget_id
    )
    return jsonify(to_dict(result)), 200


@ingestion_bp.post("/<uuid:project_id>/budgets/<uuid:budget_id>/approve")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def approve_budget(project_id: UUID, budget_id: UUID):
    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.approve_budget_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        budget_id=budget_id,
        ip_address=_ip_address(),
    )
    return jsonify(to_dict(result)), 200


@ingestion_bp.post("/<uuid:project_id>/budgets/<uuid:budget_id>/proforma")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def generate_proforma(project_id: UUID, budget_id: UUID):
    """UC17 — Fatura proforma."""
    try:
        data = GenerateProformaSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.generate_proforma_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        budget_id=budget_id,
        client_name=data.get("client_name"),
        client_tax_id=data.get("client_tax_id"),
        notes=data.get("notes"),
        ip_address=_ip_address(),
    )
    return jsonify(to_dict(result)), 201


@ingestion_bp.get("/<uuid:project_id>/proformas")
@require_auth
def list_proformas(project_id: UUID):
    """UC17 — Listar faturas proforma do projecto."""
    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.list_proformas_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
    )
    return jsonify(to_dict(result)), 200


@ingestion_bp.get("/<uuid:project_id>/audit-trail")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def get_audit_trail(project_id: UUID):
    """UC18 — Audit trail."""
    limit = min(int(request.args.get("limit", 50)), 100)
    offset = max(int(request.args.get("offset", 0)), 0)
    container: Container = ingestion_bp.container  # type: ignore[attr-defined]
    result = container.get_audit_trail_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        entity_type=request.args.get("entity_type"),
        limit=limit,
        offset=offset,
    )
    return jsonify(to_dict(result)), 200
