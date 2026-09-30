from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.value_objects.financial_assumptions import CashFlowProjection, FinancialAssumptions


@dataclass
class IndicatorResult:
    key: str
    label: str
    value: float | None
    unit: str
    category: str


@dataclass
class FinancialAnalysisResult:
    indicators: list[IndicatorResult]
    indicators_by_category: dict[str, list[dict]]
    cash_flows: CashFlowProjection
    summary: dict


class IFinancialCalculator(ABC):
    """Contrato do motor de cálculo financeiro (Strategy)."""

    @abstractmethod
    def build_cash_flows(
        self, assumptions: FinancialAssumptions, horizon_years: int, initial_investment: float
    ) -> CashFlowProjection:
        ...

    @abstractmethod
    def calculate_indicators(
        self,
        assumptions: FinancialAssumptions,
        cash_flows: CashFlowProjection,
        initial_investment: float,
        horizon_years: int,
    ) -> FinancialAnalysisResult:
        ...
