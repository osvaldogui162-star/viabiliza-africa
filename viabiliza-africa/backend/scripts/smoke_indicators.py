"""Smoke test rápido do módulo de indicadores."""
from decimal import Decimal

from app.application.services.analysis_context_builder import AnalysisContextBuilder
from app.infrastructure.financial.viability_calculator import ViabilityCalculator


class FakeProject:
    investment_amount = Decimal("2500000")
    project_horizon_years = 5
    discount_rate = Decimal("12")


def main() -> None:
    builder = AnalysisContextBuilder()
    project = FakeProject()
    assumptions = builder.build_assumptions(project, [], None, None)
    investment = builder.resolve_investment(project, [], assumptions.to_dict())
    assert isinstance(investment, float)
    calc = ViabilityCalculator()
    cash_flows = calc.build_cash_flows(assumptions, 5, investment)
    result = calc.calculate_indicators(assumptions, cash_flows, investment, 5)
    print(f"OK indicators={len(result.indicators)} inv={investment}")
    assert len(result.indicators) >= 60


if __name__ == "__main__":
    main()
