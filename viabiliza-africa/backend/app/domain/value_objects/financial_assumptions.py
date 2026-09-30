from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class FinancialAssumptions:
    """Pressupostos financeiros para análise de viabilidade."""

    annual_revenue_year1: Decimal
    revenue_growth_rate: Decimal = Decimal("8")       # %
    opex_growth_rate: Decimal = Decimal("5")          # %
    tax_rate: Decimal = Decimal("25")                 # %
    inflation_rate: Decimal = Decimal("10")           # %
    discount_rate: Decimal = Decimal("12")            # %
    debt_ratio: Decimal = Decimal("40")               # % do investimento
    interest_rate: Decimal = Decimal("15")            # %
    equity_amount: Decimal | None = None
    depreciation_years: int = 5
    salvage_value_pct: Decimal = Decimal("10")        # % do CAPEX
    working_capital_pct: Decimal = Decimal("5")     # % da receita
    capex_total: Decimal | None = None
    opex_annual: Decimal | None = None

    def to_dict(self) -> dict:
        return {
            "annual_revenue_year1": str(self.annual_revenue_year1),
            "revenue_growth_rate": str(self.revenue_growth_rate),
            "opex_growth_rate": str(self.opex_growth_rate),
            "tax_rate": str(self.tax_rate),
            "inflation_rate": str(self.inflation_rate),
            "discount_rate": str(self.discount_rate),
            "debt_ratio": str(self.debt_ratio),
            "interest_rate": str(self.interest_rate),
            "equity_amount": str(self.equity_amount) if self.equity_amount else None,
            "depreciation_years": self.depreciation_years,
            "salvage_value_pct": str(self.salvage_value_pct),
            "working_capital_pct": str(self.working_capital_pct),
            "capex_total": str(self.capex_total) if self.capex_total else None,
            "opex_annual": str(self.opex_annual) if self.opex_annual else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FinancialAssumptions":
        def dec(key: str, default: str = "0") -> Decimal:
            val = data.get(key)
            return Decimal(str(val)) if val is not None else Decimal(default)

        eq = data.get("equity_amount")
        capex = data.get("capex_total")
        opex = data.get("opex_annual")
        return cls(
            annual_revenue_year1=dec("annual_revenue_year1"),
            revenue_growth_rate=dec("revenue_growth_rate", "8"),
            opex_growth_rate=dec("opex_growth_rate", "5"),
            tax_rate=dec("tax_rate", "25"),
            inflation_rate=dec("inflation_rate", "10"),
            discount_rate=dec("discount_rate", "12"),
            debt_ratio=dec("debt_ratio", "40"),
            interest_rate=dec("interest_rate", "15"),
            equity_amount=Decimal(str(eq)) if eq else None,
            depreciation_years=int(data.get("depreciation_years", 5)),
            salvage_value_pct=dec("salvage_value_pct", "10"),
            working_capital_pct=dec("working_capital_pct", "5"),
            capex_total=Decimal(str(capex)) if capex else None,
            opex_annual=Decimal(str(opex)) if opex else None,
        )


@dataclass
class CashFlowProjection:
    """Projeção anual de fluxos de caixa."""

    years: list[int] = field(default_factory=list)
    revenue: list[float] = field(default_factory=list)
    opex: list[float] = field(default_factory=list)
    ebitda: list[float] = field(default_factory=list)
    depreciation: list[float] = field(default_factory=list)
    ebit: list[float] = field(default_factory=list)
    interest: list[float] = field(default_factory=list)
    ebt: list[float] = field(default_factory=list)
    tax: list[float] = field(default_factory=list)
    net_income: list[float] = field(default_factory=list)
    free_cash_flow: list[float] = field(default_factory=list)
    cumulative_fcf: list[float] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "years": self.years,
            "revenue": self.revenue,
            "opex": self.opex,
            "ebitda": self.ebitda,
            "depreciation": self.depreciation,
            "ebit": self.ebit,
            "interest": self.interest,
            "ebt": self.ebt,
            "tax": self.tax,
            "net_income": self.net_income,
            "free_cash_flow": self.free_cash_flow,
            "cumulative_fcf": self.cumulative_fcf,
        }
