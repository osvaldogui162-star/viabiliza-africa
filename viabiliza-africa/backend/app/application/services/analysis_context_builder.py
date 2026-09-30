from decimal import Decimal, InvalidOperation

from app.domain.entities.cost_item import CostItem
from app.domain.entities.project import Project
from app.domain.enums.cost_item_type import CostItemType
from app.domain.value_objects.financial_assumptions import FinancialAssumptions


def _as_decimal(value, default: str = "0") -> Decimal:
    """Converte qualquer valor numérico/string para Decimal de forma segura."""
    if value is None:
        return Decimal(default)
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value).strip().replace(",", "."))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default)


class AnalysisContextBuilder:
    """Constrói pressupostos e investimento a partir do projecto e custos."""

    def build_assumptions(
        self,
        project: Project,
        cost_items: list[CostItem],
        overrides: dict | None = None,
        saved: dict | None = None,
    ) -> FinancialAssumptions:
        capex_total = sum(
            (_as_decimal(i.total_amount) for i in cost_items if i.item_type == CostItemType.CAPEX),
            Decimal("0"),
        )
        opex_annual = sum(
            (_as_decimal(i.total_amount) for i in cost_items if i.item_type == CostItemType.OPEX),
            Decimal("0"),
        )

        base_data: dict = {}
        if isinstance(saved, dict):
            base_data.update(saved)
        if isinstance(overrides, dict):
            base_data.update(overrides)

        if "annual_revenue_year1" not in base_data:
            investment = self.resolve_investment_decimal(project, cost_items, base_data)
            base_data["annual_revenue_year1"] = str(
                investment * Decimal("1.5") if investment > 0 else Decimal("1000000")
            )

        if "capex_total" not in base_data and capex_total > 0:
            base_data["capex_total"] = str(capex_total)
        if "opex_annual" not in base_data and opex_annual > 0:
            base_data["opex_annual"] = str(opex_annual)

        if project.discount_rate is not None and "discount_rate" not in base_data:
            base_data["discount_rate"] = str(project.discount_rate)

        return FinancialAssumptions.from_dict(base_data)

    def resolve_investment_decimal(
        self,
        project: Project,
        cost_items: list[CostItem],
        assumptions_data: dict | None = None,
    ) -> Decimal:
        if assumptions_data and assumptions_data.get("capex_total") not in (None, ""):
            return _as_decimal(assumptions_data["capex_total"])

        capex_total = sum(
            (_as_decimal(i.total_amount) for i in cost_items if i.item_type == CostItemType.CAPEX),
            Decimal("0"),
        )
        if capex_total > 0:
            return capex_total
        return _as_decimal(getattr(project, "investment_amount", 0))

    def resolve_investment(
        self,
        project: Project,
        cost_items: list[CostItem],
        assumptions_data: dict | None = None,
    ) -> float:
        """Retorna float para os motores financeiros (VPL/TIR/Monte Carlo)."""
        return float(self.resolve_investment_decimal(project, cost_items, assumptions_data))
