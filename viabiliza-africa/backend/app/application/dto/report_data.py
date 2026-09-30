from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID


@dataclass
class ReportProjectData:
    id: UUID
    name: str
    description: str | None
    company_name: str
    company_tax_id: str | None
    sector: str
    country: str
    currency: str
    investment_amount: Decimal
    horizon_years: int
    discount_rate: Decimal | None
    status: str
    owner_name: str | None = None


@dataclass
class ReportDataBundle:
    """Pacote completo de dados para geração institucional de relatórios."""

    project: ReportProjectData
    cost_items: list[dict] = field(default_factory=list)
    capex_total: Decimal = Decimal("0")
    opex_total: Decimal = Decimal("0")
    budgets: list[dict] = field(default_factory=list)
    latest_analysis: dict | None = None
    indicators: list[dict] = field(default_factory=list)
    indicators_summary: dict = field(default_factory=dict)
    cash_flows: dict = field(default_factory=dict)
    monte_carlo: dict | None = None
    sensitivity: dict | None = None
    benchmarks: list[dict] = field(default_factory=list)
    audit_trail_count: int = 0
    audit_trail_sample: list[dict] = field(default_factory=list)
    tasks_summary: dict = field(default_factory=dict)
    report_currency: str = "AOA"
    report_language: str = "pt"
    exchange_rate: float = 1.0
