from uuid import UUID

from app.application.interfaces.monte_carlo_engine import IMonteCarloEngine
from app.application.services.analysis_access_policy import AnalysisAccessPolicy
from app.application.services.subscription_service import SubscriptionService
from app.application.services.analysis_context_builder import AnalysisContextBuilder
from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.use_cases.analysis.mappers import to_monte_carlo_output
from app.domain.exceptions.domain_exceptions import AuthorizationError, ValidationError
from app.domain.repositories.analysis_repository import (
    IFinancialAnalysisRepository,
    IFinancialAssumptionsRepository,
    IMonteCarloRepository,
)
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.infrastructure.financial.monte_carlo_engine import NumpyMonteCarloEngine


class RunMonteCarloUseCase:
    """UC20 — Simulação Monte Carlo (1.000–50.000 iterações)."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        analysis_policy: AnalysisAccessPolicy,
        context_builder: AnalysisContextBuilder,
        cost_item_repository: ICostItemRepository,
        assumptions_repository: IFinancialAssumptionsRepository,
        analysis_repository: IFinancialAnalysisRepository,
        monte_carlo_repository: IMonteCarloRepository,
        engine: IMonteCarloEngine,
        subscription_service: SubscriptionService | None = None,
    ) -> None:
        self._ctx = context_resolver
        self._policy = analysis_policy
        self._builder = context_builder
        self._items = cost_item_repository
        self._assumptions_repo = assumptions_repository
        self._analysis_repo = analysis_repository
        self._monte_carlo_repo = monte_carlo_repository
        self._engine = engine
        self._subscriptions = subscription_service

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        iterations: int = 10000,
        variable_std_devs: dict[str, float] | None = None,
        analysis_id: UUID | None = None,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_execute_analysis(ctx.actor, ctx.project):
            raise AuthorizationError("Não tem permissão para executar Monte Carlo")

        if iterations < NumpyMonteCarloEngine.MIN_ITERATIONS or iterations > NumpyMonteCarloEngine.MAX_ITERATIONS:
            raise ValidationError(
                f"Iterações devem estar entre {NumpyMonteCarloEngine.MIN_ITERATIONS} "
                f"e {NumpyMonteCarloEngine.MAX_ITERATIONS}"
            )

        if self._subscriptions:
            self._subscriptions.ensure_monte_carlo(ctx.actor, iterations)

        cost_items = self._items.find_by_project(project_id)
        saved = self._assumptions_repo.find_by_project(project_id)
        assumptions = self._builder.build_assumptions(ctx.project, cost_items, saved=saved)
        investment = self._builder.resolve_investment(
            ctx.project, cost_items, assumptions.to_dict()
        )
        horizon = ctx.project.project_horizon_years

        if analysis_id:
            existing = self._analysis_repo.find_by_id(analysis_id)
            if existing is None or existing.project_id != project_id:
                raise ValidationError("Análise de referência inválida")

        result = self._engine.simulate(
            assumptions, horizon, investment, iterations, variable_std_devs
        )

        parameters = {
            "iterations": iterations,
            "variable_std_devs": variable_std_devs or {},
            "horizon_years": horizon,
            "initial_investment": investment,
        }
        results_payload = {
            "statistics": result.statistics,
            "probability_npv_positive": result.probability_npv_positive,
            "percentiles": result.percentiles,
            "npv_sample_size": len(result.npv_distribution),
            "npv_distribution_sample": result.npv_distribution,
        }

        sim = self._monte_carlo_repo.create(
            project_id=project_id,
            iterations=iterations,
            parameters=parameters,
            results=results_payload,
            analysis_id=analysis_id,
            created_by=actor_id,
        )
        return to_monte_carlo_output(sim)


class ListMonteCarloUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        analysis_policy: AnalysisAccessPolicy,
        monte_carlo_repository: IMonteCarloRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = analysis_policy
        self._repo = monte_carlo_repository

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_view_analysis(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para visualizar simulações")

        items = self._repo.find_by_project(project_id)
        return {
            "items": [to_monte_carlo_output(s) for s in items],
            "total": len(items),
        }
