"""Cenários optimista, base e pessimista."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from app.application.interfaces.financial_calculator import IFinancialCalculator
from app.application.services.analysis_access_policy import AnalysisAccessPolicy
from app.application.services.analysis_context_builder import AnalysisContextBuilder
from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.services.subscription_service import SubscriptionService
from app.domain.exceptions.domain_exceptions import AuthorizationError
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.value_objects.financial_assumptions import FinancialAssumptions
from app.infrastructure.financial import financial_math as fm


class RunScenarioAnalysisUseCase:
    SCENARIOS = (
        ("optimistic", "Optimista", Decimal("15"), Decimal("-8")),
        ("base", "Base", Decimal("0"), Decimal("0")),
        ("pessimistic", "Pessimista", Decimal("-15"), Decimal("12")),
    )

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        analysis_policy: AnalysisAccessPolicy,
        context_builder: AnalysisContextBuilder,
        project_repository: IProjectRepository,
        cost_item_repository: ICostItemRepository,
        calculator: IFinancialCalculator,
        subscription_service: SubscriptionService | None = None,
    ) -> None:
        self._ctx = context_resolver
        self._policy = analysis_policy
        self._builder = context_builder
        self._projects = project_repository
        self._items = cost_item_repository
        self._calculator = calculator
        self._subscriptions = subscription_service

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_execute_analysis(ctx.actor, ctx.project):
            raise AuthorizationError("Não tem permissão para simular cenários")
        if self._subscriptions:
            self._subscriptions.ensure_sensitivity(ctx.actor)

        cost_items = self._items.find_by_project(project_id)
        base_assumptions = self._builder.build_assumptions(ctx.project, cost_items)
        investment = self._builder.resolve_investment(
            ctx.project, cost_items, base_assumptions.to_dict()
        )
        horizon = ctx.project.project_horizon_years
        rate = float(base_assumptions.discount_rate) / 100

        scenarios = []
        for code, label, rev_delta, opex_delta in self.SCENARIOS:
            assumptions = self._apply_deltas(base_assumptions, rev_delta, opex_delta)
            cash_flows = self._calculator.build_cash_flows(assumptions, horizon, investment)
            fcf = cash_flows.free_cash_flow
            npv = fm.npv(rate, fcf)
            irr = fm.irr(fcf)
            payback = fm.payback_period(fcf)
            scenarios.append(
                {
                    "code": code,
                    "label": label,
                    "revenue_adjustment_pct": str(rev_delta),
                    "opex_adjustment_pct": str(opex_delta),
                    "npv": round(npv, 2),
                    "irr": round(irr, 4) if irr is not None else None,
                    "payback_years": round(payback, 2) if payback is not None else None,
                    "total_revenue": round(sum(cash_flows.revenue[1:]), 2),
                    "total_fcf": round(sum(fcf[1:]), 2),
                }
            )

        return {
            "project_id": str(project_id),
            "investment": str(investment),
            "horizon_years": horizon,
            "scenarios": scenarios,
        }

    @staticmethod
    def _apply_deltas(
        base: FinancialAssumptions,
        revenue_delta_pct: Decimal,
        opex_delta_pct: Decimal,
    ) -> FinancialAssumptions:
        rev_factor = Decimal("1") + revenue_delta_pct / Decimal("100")
        opex_factor = Decimal("1") + opex_delta_pct / Decimal("100")
        data = base.to_dict()
        data["annual_revenue_year1"] = str(
            (Decimal(data["annual_revenue_year1"]) * rev_factor).quantize(Decimal("0.01"))
        )
        if data.get("opex_annual"):
            data["opex_annual"] = str(
                (Decimal(data["opex_annual"]) * opex_factor).quantize(Decimal("0.01"))
            )
        data["revenue_growth_rate"] = str(
            (Decimal(data["revenue_growth_rate"]) + revenue_delta_pct / Decimal("2")).quantize(
                Decimal("0.01")
            )
        )
        return FinancialAssumptions.from_dict(data)
