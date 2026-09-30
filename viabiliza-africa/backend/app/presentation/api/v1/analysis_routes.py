from uuid import UUID

from flask import Blueprint, g, jsonify, request, send_file
from io import BytesIO
from marshmallow import ValidationError as MarshmallowValidationError

from app.di.container import Container
from app.domain.enums.user_role import UserRole
from app.presentation.decorators.rbac import require_auth, require_roles
from app.presentation.schemas.analysis_schemas import (
    CalculateIndicatorsSchema,
    MonteCarloSchema,
    SensitivitySchema,
)
from app.presentation.serializers import to_dict


analysis_bp = Blueprint("analysis", __name__, url_prefix="/api/v1/projects")


def _validation_error(exc: MarshmallowValidationError):
    return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400


def _assumptions_dict(data: dict) -> dict | None:
    raw = data.get("assumptions")
    if not raw:
        return None
    return {k: str(v) if v is not None else None for k, v in raw.items()}


@analysis_bp.post("/<uuid:project_id>/analysis/indicators")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def calculate_indicators(project_id: UUID):
    """UC19 — Calcular indicadores de viabilidade."""
    try:
        data = CalculateIndicatorsSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = analysis_bp.container  # type: ignore[attr-defined]
    result = container.calculate_indicators_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        assumptions_overrides=_assumptions_dict(data),
    )
    return jsonify(to_dict(result)), 201


@analysis_bp.get("/<uuid:project_id>/analysis/indicators")
@require_auth
def list_analyses(project_id: UUID):
    container: Container = analysis_bp.container  # type: ignore[attr-defined]
    limit = min(int(request.args.get("limit", 20)), 50)
    result = container.list_analyses_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        limit=limit,
    )
    return jsonify(result), 200


@analysis_bp.get("/<uuid:project_id>/analysis/indicators/export")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def export_indicators(project_id: UUID):
    """UC23 — Exportar indicadores para Excel."""
    analysis_id = request.args.get("analysis_id")
    language = request.args.get("lang", "pt")
    container: Container = analysis_bp.container  # type: ignore[attr-defined]
    content, filename = container.export_indicators_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        analysis_id=UUID(analysis_id) if analysis_id else None,
        language=language,
    )
    return send_file(
        BytesIO(content),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename,
    )


@analysis_bp.get("/<uuid:project_id>/analysis/indicators/<uuid:analysis_id>")
@require_auth
def get_analysis(project_id: UUID, analysis_id: UUID):
    container: Container = analysis_bp.container  # type: ignore[attr-defined]
    result = container.get_analysis_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        analysis_id=analysis_id,
    )
    return jsonify(to_dict(result)), 200


@analysis_bp.post("/<uuid:project_id>/analysis/monte-carlo")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def run_monte_carlo(project_id: UUID):
    """UC20 — Simulação Monte Carlo."""
    try:
        data = MonteCarloSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = analysis_bp.container  # type: ignore[attr-defined]
    result = container.run_monte_carlo_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        iterations=data["iterations"],
        variable_std_devs=data.get("variable_std_devs"),
        analysis_id=data.get("analysis_id"),
    )
    return jsonify(to_dict(result)), 201


@analysis_bp.get("/<uuid:project_id>/analysis/monte-carlo")
@require_auth
def list_monte_carlo(project_id: UUID):
    container: Container = analysis_bp.container  # type: ignore[attr-defined]
    result = container.list_monte_carlo_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
    )
    return jsonify(result), 200


@analysis_bp.post("/<uuid:project_id>/analysis/sensitivity")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def run_sensitivity(project_id: UUID):
    """UC21 — Análise de sensibilidade."""
    try:
        data = SensitivitySchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return _validation_error(exc)

    container: Container = analysis_bp.container  # type: ignore[attr-defined]
    result = container.run_sensitivity_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
        variables=data.get("variables"),
        analysis_id=data.get("analysis_id"),
    )
    return jsonify(to_dict(result)), 201


@analysis_bp.get("/<uuid:project_id>/analysis/sensitivity")
@require_auth
def list_sensitivity(project_id: UUID):
    container: Container = analysis_bp.container  # type: ignore[attr-defined]
    result = container.list_sensitivity_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
    )
    return jsonify(result), 200


@analysis_bp.post("/<uuid:project_id>/analysis/scenarios")
@require_roles(UserRole.ADMIN, UserRole.FINANCIAL)
def run_scenarios(project_id: UUID):
    """Simular cenários optimista, base e pessimista."""
    container: Container = analysis_bp.container  # type: ignore[attr-defined]
    result = container.run_scenario_analysis_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
    )
    return jsonify(result), 200


@analysis_bp.get("/<uuid:project_id>/analysis/benchmarks")
@require_auth
def compare_benchmarks(project_id: UUID):
    """UC22 — Comparar benchmarks de mercado."""
    container: Container = analysis_bp.container  # type: ignore[attr-defined]
    result = container.compare_benchmarks_use_case.execute(
        actor_id=g.current_user.id,
        project_id=project_id,
    )
    return jsonify(result), 200
