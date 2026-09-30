from uuid import UUID

from app.application.interfaces.sensitivity_engine import ISensitivityEngine, SensitivityVariable
from app.application.services.analysis_access_policy import AnalysisAccessPolicy
from app.application.services.analysis_context_builder import AnalysisContextBuilder
from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.services.subscription_service import SubscriptionService
from app.application.use_cases.analysis.mappers import to_sensitivity_output
from app.domain.exceptions.domain_exceptions import AuthorizationError, ValidationError
from app.domain.repositories.analysis_repository import (
    IFinancialAnalysisRepository,
    IFinancialAssumptionsRepository,
    ISensitivityRepository,
)
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.infrastructure.financial.sensitivity_engine import TornadoSensitivityEngine


class RunSensitivityUseCase:
    """UC21 — Análise de sensibilidade (3–10 variáveis)."""

    DEFAULT_VARIABLES = [
        ("annual_revenue_year1", "Receita Ano 1", -10, 10),
        ("revenue_growth_rate", "Crescimento Receita", -20, 20),
        ("opex_growth_rate", "Crescimento OPEX", -15, 15),
        ("discount_rate", "Taxa de Desconto", -2, 2),
        ("tax_rate", "Taxa de Imposto", -5, 5),
    ]

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        analysis_policy: AnalysisAccessPolicy,
        context_builder: AnalysisContextBuilder,
        cost_item_repository: ICostItemRepository,
        assumptions_repository: IFinancialAssumptionsRepository,
        analysis_repository: IFinancialAnalysisRepository,
        sensitivity_repository: ISensitivityRepository,
        engine: ISensitivityEngine,
        subscription_service: SubscriptionService | None = None,
    ) -> None:
        self._ctx = context_resolver
        self._policy = analysis_policy
        self._builder = context_builder
        self._items = cost_item_repository
        self._assumptions_repo = assumptions_repository
        self._analysis_repo = analysis_repository
        self._sensitivity_repo = sensitivity_repository
        self._engine = engine
        self._subscription = subscription_service

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        variables: list[dict] | None = None,
        analysis_id: UUID | None = None,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_execute_analysis(ctx.actor, ctx.project):
            raise AuthorizationError("Não tem permissão para análise de sensibilidade")

        if self._subscription:
            self._subscription.ensure_sensitivity(ctx.actor)

        cost_items = self._items.find_by_project(project_id)
        saved = self._assumptions_repo.find_by_project(project_id)
        assumptions = self._builder.build_assumptions(ctx.project, cost_items, saved=saved)
        investment = self._builder.resolve_investment(
            ctx.project, cost_items, assumptions.to_dict()
        )
        horizon = ctx.project.project_horizon_years

        sens_vars = self._build_variables(assumptions.to_dict(), variables)
        if len(sens_vars) < TornadoSensitivityEngine.MIN_VARIABLES:
            raise ValidationError(
                f"Mínimo de {TornadoSensitivityEngine.MIN_VARIABLES} variáveis"
            )
        if len(sens_vars) > TornadoSensitivityEngine.MAX_VARIABLES:
            raise ValidationError(
                f"Máximo de {TornadoSensitivityEngine.MAX_VARIABLES} variáveis"
            )

        if analysis_id:
            existing = self._analysis_repo.find_by_id(analysis_id)
            if existing is None or existing.project_id != project_id:
                raise ValidationError("Análise de referência inválida")

        result = self._engine.analyze(assumptions, horizon, investment, sens_vars)

        variables_payload = {"items": result.variables}
        results_payload = {
            "base_npv": result.base_npv,
            "base_irr": result.base_irr,
            "tornado_npv": result.tornado_npv,
            "tornado_irr": result.tornado_irr,
        }

        analysis = self._sensitivity_repo.create(
            project_id=project_id,
            variables=variables_payload,
            results=results_payload,
            analysis_id=analysis_id,
            created_by=actor_id,
        )
        return to_sensitivity_output(analysis)

    def _build_variables(
        self, assumptions: dict, overrides: list[dict] | None
    ) -> list[SensitivityVariable]:
        if overrides:
            return [
                SensitivityVariable(
                    key=v["key"],
                    label=v.get("label", v["key"]),
                    base_value=float(assumptions.get(v["key"], v.get("base_value", 0))),
                    shock_low_pct=float(v.get("shock_low_pct", -10)),
                    shock_high_pct=float(v.get("shock_high_pct", 10)),
                )
                for v in overrides
            ]

        items: list[SensitivityVariable] = []
        for key, label, low, high in self.DEFAULT_VARIABLES:
            if key in assumptions:
                items.append(
                    SensitivityVariable(
                        key=key,
                        label=label,
                        base_value=float(assumptions[key]),
                        shock_low_pct=low,
                        shock_high_pct=high,
                    )
                )
        return items


class ListSensitivityUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        analysis_policy: AnalysisAccessPolicy,
        sensitivity_repository: ISensitivityRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = analysis_policy
        self._repo = sensitivity_repository

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_view_analysis(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para visualizar sensibilidade")

        items = self._repo.find_by_project(project_id)
        return {
            "items": [to_sensitivity_output(a) for a in items],
            "total": len(items),
        }
