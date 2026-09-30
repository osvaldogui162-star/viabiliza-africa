import json
from uuid import UUID

from app.application.interfaces.financial_calculator import IFinancialCalculator
from app.application.interfaces.hash_service import IHashService
from app.application.services.analysis_access_policy import AnalysisAccessPolicy
from app.application.services.analysis_context_builder import AnalysisContextBuilder
from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.use_cases.analysis.mappers import to_analysis_output
from app.domain.exceptions.domain_exceptions import AuthorizationError, ValidationError
from app.domain.repositories.analysis_repository import (
    IFinancialAnalysisRepository,
    IFinancialAssumptionsRepository,
)
from app.domain.repositories.cost_item_repository import ICostItemRepository


class CalculateIndicatorsUseCase:
    """UC19 — Calcular 60+ indicadores de viabilidade."""

    MIN_INDICATORS = 60

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        analysis_policy: AnalysisAccessPolicy,
        context_builder: AnalysisContextBuilder,
        cost_item_repository: ICostItemRepository,
        assumptions_repository: IFinancialAssumptionsRepository,
        analysis_repository: IFinancialAnalysisRepository,
        calculator: IFinancialCalculator,
        hash_service: IHashService,
    ) -> None:
        self._ctx = context_resolver
        self._policy = analysis_policy
        self._builder = context_builder
        self._items = cost_item_repository
        self._assumptions_repo = assumptions_repository
        self._analysis_repo = analysis_repository
        self._calculator = calculator
        self._hash = hash_service

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        assumptions_overrides: dict | None = None,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_execute_analysis(ctx.actor, ctx.project):
            raise AuthorizationError("Não tem permissão para calcular indicadores")

        cost_items = self._items.find_by_project(project_id)
        saved = self._assumptions_repo.find_by_project(project_id)
        assumptions = self._builder.build_assumptions(
            ctx.project, cost_items, overrides=assumptions_overrides, saved=saved
        )
        investment = self._builder.resolve_investment(
            ctx.project, cost_items, assumptions.to_dict()
        )
        horizon = ctx.project.project_horizon_years

        cash_flows = self._calculator.build_cash_flows(assumptions, horizon, investment)
        result = self._calculator.calculate_indicators(
            assumptions, cash_flows, investment, horizon
        )

        if len(result.indicators) < self.MIN_INDICATORS:
            raise ValidationError(
                f"Cálculo incompleto: apenas {len(result.indicators)} indicadores"
            )

        assumptions_dict = assumptions.to_dict()
        self._assumptions_repo.upsert(project_id, assumptions_dict, actor_id)

        indicators_payload = {
            "items": [
                {
                    "key": i.key,
                    "label": i.label,
                    "value": i.value,
                    "unit": i.unit,
                    "category": i.category,
                }
                for i in result.indicators
            ],
            "by_category": result.indicators_by_category,
            "summary": result.summary,
        }

        hash_input = json.dumps(
            {
                "assumptions": assumptions_dict,
                "cash_flows": cash_flows.to_dict(),
                "summary": result.summary,
            },
            sort_keys=True,
        )
        calculation_hash = self._hash.hash_string(hash_input)

        analysis = self._analysis_repo.create(
            project_id=project_id,
            assumptions=assumptions_dict,
            cash_flows=cash_flows.to_dict(),
            indicators=indicators_payload,
            indicators_count=len(result.indicators),
            calculation_hash=calculation_hash,
            created_by=actor_id,
        )

        output = to_analysis_output(analysis)
        output["summary"] = result.summary
        return output
