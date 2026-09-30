import numpy as np

from app.application.interfaces.financial_calculator import IFinancialCalculator
from app.application.interfaces.monte_carlo_engine import IMonteCarloEngine, MonteCarloResult
from app.domain.value_objects.financial_assumptions import FinancialAssumptions
from app.infrastructure.financial import financial_math as fm


class NumpyMonteCarloEngine(IMonteCarloEngine):
    """Simulação Monte Carlo com distribuição normal (UC20)."""

    DEFAULT_STDS = {
        "revenue_growth_rate": 3.0,
        "opex_growth_rate": 2.0,
        "discount_rate": 1.5,
        "annual_revenue_year1": 10.0,
    }

    def __init__(self, calculator: IFinancialCalculator) -> None:
        self._calculator = calculator

    def simulate(
        self,
        assumptions: FinancialAssumptions,
        horizon_years: int,
        initial_investment: float,
        iterations: int,
        variable_std_devs: dict[str, float] | None = None,
    ) -> MonteCarloResult:
        if iterations < self.MIN_ITERATIONS or iterations > self.MAX_ITERATIONS:
            raise ValueError(
                f"Iterações devem estar entre {self.MIN_ITERATIONS} e {self.MAX_ITERATIONS}"
            )

        stds = {**self.DEFAULT_STDS, **(variable_std_devs or {})}
        rng = np.random.default_rng()

        npv_values: list[float] = []
        rate = float(assumptions.discount_rate) / 100

        for _ in range(iterations):
            sim = self._sample_assumptions(assumptions, stds, rng)
            cf = self._calculator.build_cash_flows(sim, horizon_years, initial_investment)
            npv_values.append(fm.npv(rate, cf.free_cash_flow))

        arr = np.array(npv_values)
        positive = float(np.sum(arr > 0) / len(arr) * 100)

        percentiles = {
            "p5": float(np.percentile(arr, 5)),
            "p25": float(np.percentile(arr, 25)),
            "p50": float(np.percentile(arr, 50)),
            "p75": float(np.percentile(arr, 75)),
            "p95": float(np.percentile(arr, 95)),
        }

        statistics = {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "median": float(np.median(arr)),
        }

        return MonteCarloResult(
            iterations=iterations,
            npv_distribution=[round(v, 2) for v in npv_values[:500]],
            statistics=statistics,
            probability_npv_positive=round(positive, 2),
            percentiles=percentiles,
        )

    def _sample_assumptions(
        self,
        base: FinancialAssumptions,
        stds: dict[str, float],
        rng: np.random.Generator,
    ) -> FinancialAssumptions:
        data = base.to_dict()

        def sample_pct(key: str, min_val: float = 0.0) -> None:
            if key not in stds:
                return
            val = float(data[key]) + rng.normal(0, stds[key])
            data[key] = str(max(min_val, val))

        def sample_amount(key: str) -> None:
            if key not in stds:
                return
            val = float(data[key]) * (1 + rng.normal(0, stds[key] / 100))
            data[key] = str(max(0, val))

        sample_pct("revenue_growth_rate")
        sample_pct("opex_growth_rate")
        sample_pct("discount_rate", min_val=1.0)
        sample_amount("annual_revenue_year1")

        return FinancialAssumptions.from_dict(data)
