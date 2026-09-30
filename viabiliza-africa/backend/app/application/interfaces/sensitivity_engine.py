from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.value_objects.financial_assumptions import FinancialAssumptions


@dataclass
class SensitivityVariable:
    key: str
    label: str
    base_value: float
    shock_low_pct: float
    shock_high_pct: float


@dataclass
class SensitivityResult:
    variables: list[dict]
    base_npv: float
    base_irr: float | None
    tornado_npv: list[dict]
    tornado_irr: list[dict]


class ISensitivityEngine(ABC):
    MIN_VARIABLES = 3
    MAX_VARIABLES = 10

    @abstractmethod
    def analyze(
        self,
        assumptions: FinancialAssumptions,
        horizon_years: int,
        initial_investment: float,
        variables: list[SensitivityVariable],
    ) -> SensitivityResult:
        ...
