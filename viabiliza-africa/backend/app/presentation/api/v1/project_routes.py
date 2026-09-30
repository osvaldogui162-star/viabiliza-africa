from decimal import Decimal
from uuid import UUID

from flask import Blueprint, g, jsonify, request
from marshmallow import ValidationError as MarshmallowValidationError

from app.application.dto.project_dto import (
    CreateProjectInput,
    ListProjectsInput,
    RemoveProjectShareInput,
    ShareProjectInput,
    UpdateProjectInput,
)
from app.application.use_cases.projects.project_mapper import summarize_project_spend
from app.di.container import Container
from app.domain.catalog.angola_admin_divisions import list_municipalities, list_provinces
from app.domain.enums.country import Country
from app.domain.enums.currency import Currency
from app.domain.enums.financing_bank import FinancingBank
from app.domain.enums.financing_type import FinancingType
from app.domain.enums.project_sector import ProjectSector
from app.domain.enums.project_status import ProjectStatus
from app.domain.enums.share_permission import SharePermission
from app.domain.enums.user_role import UserRole
from app.infrastructure.geocoding.location_geocoder import LocationGeocoder
from app.presentation.decorators.rbac import require_auth, require_roles
from app.presentation.schemas.project_schemas import (
    CreateProjectSchema,
    GeocodeLocationSchema,
    ShareProjectSchema,
    UpdateProjectSchema,
)
from app.presentation.serializers import to_dict


projects_bp = Blueprint("projects", __name__, url_prefix="/api/v1/projects")


def _client_meta() -> dict:
    return {
        "ip_address": request.headers.get("X-Forwarded-For", request.remote_addr),
        "user_agent": request.headers.get("User-Agent"),
    }


def _parse_pagination() -> tuple[int, int]:
    limit = min(int(request.args.get("limit", 20)), 100)
    offset = max(int(request.args.get("offset", 0)), 0)
    return limit, offset


def _validation_error(exc: MarshmallowValidationError):
    details = exc.messages
    if isinstance(details, dict):
        parts: list[str] = []
        for field, messages in details.items():
            if isinstance(messages, (list, tuple)):
                parts.append(f"{field}: {'; '.join(str(m) for m in messages)}")
            else:
                parts.append(f"{field}: {messages}")
        message = "; ".join(parts) if parts else "Dados inválidos"
    else:
        message = str(details) if details else "Dados inválidos"
    return jsonify(
        {"error": {"code": "validation_error", "message": message, "details": details}}
    ), 400


@projects_bp.get("/metadata")
@require_auth
def get_metadata():
    """Opções para formulários do frontend (setores, países, moedas, bancos, status)."""
    return jsonify(
        {
            "sectors": [
                {"value": s.value, "label": s.label_pt} for s in ProjectSector
            ],
            "countries": [
                {"value": c.value, "label": c.label_pt} for c in Country
            ],
            "currencies": [{"value": c.value, "label": c.value} for c in Currency],
            "statuses": [
                {"value": s.value, "label": s.label_pt} for s in ProjectStatus
            ],
            "share_permissions": [
                {"value": p.value, "label": p.value} for p in SharePermission
            ],
            "banks": [
                {
                    "value": b.value,
                    "label": b.label_pt,
                    "website": b.website,
                    "logo": b.logo_path,
                }
                for b in FinancingBank
            ],
            "provinces": list_provinces(),
            "financing_types": [
                {"value": f.value, "label": f.label_pt} for f in FinancingType
            ],
        }
    ), 200


@projects_bp.get("/metadata/municipalities")
@require_auth
def get_municipalities():
    """Municípios por província (catálogo INE)."""
    province = request.args.get("province", "").strip()
    if not province:
        return jsonify({"error": {"code": "validation_error", "message": "province é obrigatório"}}), 400
    return jsonify({"municipalities": list_municipalities(province)}), 200


@projects_bp.post("/geocode")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def geocode_location():
    """Valida localização angolana via Google Maps (se configurado) ou catálogo INE."""
    try:
        data = GeocodeLocationSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = projects_bp.container  # type: ignore[attr-defined]
    geocoder = LocationGeocoder(google_maps_api_key=container.config.GOOGLE_MAPS_API_KEY)
    try:
        result = geocoder.geocode(
            province_code=data["province"],
            municipality_code=data["municipality"],
            address=data.get("address"),
        )
    except ValueError as exc:
        return jsonify({"error": {"code": "validation_error", "message": str(exc)}}), 400

    return jsonify(
        {
            "latitude": str(result.latitude),
            "longitude": str(result.longitude),
            "formatted_address": result.formatted_address,
            "source": result.source,
            "verified": result.verified,
        }
    ), 200


@projects_bp.post("")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def create_project():
    """UC06 — Criar novo projeto."""
    try:
        data = CreateProjectSchema().load(request.get_json() or {})
        CreateProjectSchema.validate_location(data)
    except MarshmallowValidationError as exc:
        if isinstance(exc.messages, str):
            return jsonify({"error": {"code": "validation_error", "message": exc.messages}}), 400
        return _validation_error(exc)

    container: Container = projects_bp.container  # type: ignore[attr-defined]
    result = container.create_project_use_case.execute(
        CreateProjectInput(
            actor_id=g.current_user.id,
            name=data["name"],
            description=data.get("description"),
            company_name=data["company_name"],
            company_tax_id=data.get("company_tax_id"),
            sector=data["sector"],
            country=data["country"],
            currency=data["currency"],
            investment_amount=Decimal(str(data["investment_amount"])),
            project_horizon_years=data.get("project_horizon_years", 5),
            discount_rate=(
                Decimal(str(data["discount_rate"])) if data.get("discount_rate") is not None else None
            ),
            bank_code=data.get("bank_code"),
            bank_rate_label=data.get("bank_rate_label"),
            bank_rate_source_url=data.get("bank_rate_source_url"),
            rep_full_name=data.get("rep_full_name"),
            rep_email=data.get("rep_email"),
            rep_id_number=data.get("rep_id_number"),
            rep_phone=data.get("rep_phone"),
            rep_role=data.get("rep_role"),
            company_province=data.get("company_province"),
            company_municipality=data.get("company_municipality"),
            company_address=data.get("company_address"),
            company_activity=data.get("company_activity"),
            company_phone=data.get("company_phone"),
            company_email=data.get("company_email"),
            company_website=data.get("company_website"),
            company_latitude=(
                Decimal(str(data["company_latitude"]))
                if data.get("company_latitude") is not None
                else None
            ),
            company_longitude=(
                Decimal(str(data["company_longitude"]))
                if data.get("company_longitude") is not None
                else None
            ),
            geocode_verified=bool(data.get("geocode_verified", False)),
            geocode_source=data.get("geocode_source"),
            financing_type=data.get("financing_type"),
            loan_term_months=data.get("loan_term_months"),
            bank_branch=data.get("bank_branch"),
            **_client_meta(),
        )
    )
    return jsonify(to_dict(result)), 201


@projects_bp.get("")
@require_auth
def list_projects():
    """UC07 — Listar projetos com filtros."""
    limit, offset = _parse_pagination()
    container: Container = projects_bp.container  # type: ignore[attr-defined]
    result = container.list_projects_use_case.execute(
        ListProjectsInput(
            actor_id=g.current_user.id,
            status=request.args.get("status"),
            country=request.args.get("country"),
            sector=request.args.get("sector"),
            search=request.args.get("search"),
            limit=limit,
            offset=offset,
        )
    )
    return jsonify(to_dict(result)), 200


@projects_bp.get("/<uuid:project_id>")
@require_auth
def get_project(project_id: UUID):
    """UC10 — Detalhes do projeto."""
    container: Container = projects_bp.container  # type: ignore[attr-defined]
    result = container.get_project_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
    )
    return jsonify(to_dict(result)), 200


@projects_bp.patch("/<uuid:project_id>")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def update_project(project_id: UUID):
    """UC08 — Editar projeto."""
    try:
        data = UpdateProjectSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = projects_bp.container  # type: ignore[attr-defined]
    result = container.update_project_use_case.execute(
        UpdateProjectInput(
            actor_id=g.current_user.id,
            project_id=project_id,
            name=data.get("name"),
            description=data.get("description"),
            company_name=data.get("company_name"),
            company_tax_id=data.get("company_tax_id"),
            sector=data.get("sector"),
            country=data.get("country"),
            currency=data.get("currency"),
            investment_amount=(
                Decimal(str(data["investment_amount"]))
                if data.get("investment_amount") is not None
                else None
            ),
            project_horizon_years=data.get("project_horizon_years"),
            discount_rate=(
                Decimal(str(data["discount_rate"]))
                if data.get("discount_rate") is not None
                else None
            ),
            bank_code=data.get("bank_code"),
            bank_rate_label=data.get("bank_rate_label"),
            bank_rate_source_url=data.get("bank_rate_source_url"),
            rep_full_name=data.get("rep_full_name"),
            rep_email=data.get("rep_email"),
            rep_id_number=data.get("rep_id_number"),
            rep_phone=data.get("rep_phone"),
            rep_role=data.get("rep_role"),
            company_province=data.get("company_province"),
            company_municipality=data.get("company_municipality"),
            company_address=data.get("company_address"),
            company_activity=data.get("company_activity"),
            company_phone=data.get("company_phone"),
            company_email=data.get("company_email"),
            company_website=data.get("company_website"),
            company_latitude=(
                Decimal(str(data["company_latitude"]))
                if data.get("company_latitude") is not None
                else None
            ),
            company_longitude=(
                Decimal(str(data["company_longitude"]))
                if data.get("company_longitude") is not None
                else None
            ),
            geocode_verified=data.get("geocode_verified"),
            geocode_source=data.get("geocode_source"),
            financing_type=data.get("financing_type"),
            loan_term_months=data.get("loan_term_months"),
            bank_branch=data.get("bank_branch"),
            **_client_meta(),
        )
    )
    return jsonify(to_dict(result)), 200


@projects_bp.delete("/<uuid:project_id>")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def delete_project(project_id: UUID):
    """UC09 — Excluir projeto (soft delete)."""
    container: Container = projects_bp.container  # type: ignore[attr-defined]
    result = container.delete_project_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        **_client_meta(),
    )
    return jsonify(result), 200


@projects_bp.get("/<uuid:project_id>/sector-profile")
@require_auth
def get_sector_profile(project_id: UUID):
    """Perfil setorial — módulo, casos de uso, catálogo e benchmarks."""
    language = request.args.get("lang", "pt")
    container: Container = projects_bp.container  # type: ignore[attr-defined]
    result = container.get_sector_profile_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        language=language,
    )
    return jsonify(result), 200


@projects_bp.post("/<uuid:project_id>/strategic-insights")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def generate_strategic_insights(project_id: UUID):
    """Gerar Missão, Visão, Valores, SWOT, riscos e incentivos AIPEX."""
    container: Container = projects_bp.container  # type: ignore[attr-defined]
    result = container.generate_strategic_insights_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
    )
    return jsonify(result), 201


@projects_bp.post("/<uuid:project_id>/shares")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def share_project(project_id: UUID):
    """UC11 — Partilhar projeto."""
    try:
        data = ShareProjectSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = projects_bp.container  # type: ignore[attr-defined]
    result = container.share_project_use_case.execute(
        ShareProjectInput(
            actor_id=g.current_user.id,
            project_id=project_id,
            user_email=data["user_email"],
            permission=data.get("permission", "view"),
            **_client_meta(),
        )
    )
    return jsonify(to_dict(result)), 201


@projects_bp.get("/<uuid:project_id>/shares")
@require_auth
def list_project_shares(project_id: UUID):
    """Listar colaboradores do projeto."""
    container: Container = projects_bp.container  # type: ignore[attr-defined]
    result = container.list_project_shares_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
    )
    return jsonify(to_dict(result)), 200


@projects_bp.delete("/<uuid:project_id>/shares/<uuid:user_id>")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def remove_project_share(project_id: UUID, user_id: UUID):
    """Remover partilha de projeto."""
    container: Container = projects_bp.container  # type: ignore[attr-defined]
    result = container.remove_project_share_use_case.execute(
        RemoveProjectShareInput(
            actor_id=g.current_user.id,
            project_id=project_id,
            target_user_id=user_id,
            **_client_meta(),
        )
    )
    return jsonify(result), 200


@projects_bp.get("/<uuid:project_id>/billing-integration")
@require_auth
def get_billing_integration(project_id: UUID):
    container: Container = projects_bp.container  # type: ignore[attr-defined]
    result = container.get_project_billing_integration_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
    )
    return jsonify(result), 200


@projects_bp.post("/<uuid:project_id>/billing-integration")
@require_auth
def configure_billing_integration(project_id: UUID):
    data = request.get_json() or {}
    container: Container = projects_bp.container  # type: ignore[attr-defined]
    result = container.configure_project_billing_integration_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        erp_label=str(data.get("erp_label", "")),
    )
    return jsonify(result), 201


@projects_bp.post("/<uuid:project_id>/billing-integration/regenerate-key")
@require_auth
def regenerate_billing_api_key(project_id: UUID):
    container: Container = projects_bp.container  # type: ignore[attr-defined]
    result = container.regenerate_project_billing_api_key_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
    )
    return jsonify(result), 200


@projects_bp.post("/<uuid:project_id>/billing-integration/sync")
@require_auth
def sync_billing_integration(project_id: UUID):
    data = request.get_json() or {}
    payload = data.get("payload") or data
    container: Container = projects_bp.container  # type: ignore[attr-defined]
    result = container.sync_project_billing_integration_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        payload=payload if isinstance(payload, dict) else {},
    )
    return jsonify(result), 200
