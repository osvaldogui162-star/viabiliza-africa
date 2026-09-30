from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.value_objects.financial_assumptions import FinancialAssumptions


@dataclass
class MonteCarloResult:
    iterations: int
    npv_distribution: list[float]
    statistics: dict
    probability_npv_positive: float
    percentiles: dict


class IMonteCarloEngine(ABC):
    MIN_ITERATIONS = 1000
    MAX_ITERATIONS = 50000

    @abstractmethod
    def simulate(
        self,
        assumptions: FinancialAssumptions,
        horizon_years: int,
        initial_investment: float,
        iterations: int,
        variable_std_devs: dict[str, float] | None = None,
    ) -> MonteCarloResult:
        ...
