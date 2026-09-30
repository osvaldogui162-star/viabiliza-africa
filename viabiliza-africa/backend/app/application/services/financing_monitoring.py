from decimal import Decimal

from app.domain.entities.cost_item import CostItem
from app.domain.entities.project import Project
from app.domain.entities.project_financing import ProjectFinancing
from app.application.use_cases.projects.project_mapper import summarize_project_spend


def compute_monitoring_status(
    *,
    approved_amount: Decimal,
    spent_total: Decimal,
    investment_amount: Decimal,
) -> str:
    if approved_amount <= 0:
        return "on_track"
    utilization = spent_total / approved_amount
    if spent_total > investment_amount or utilization > Decimal("1.05"):
        return "critical"
    if utilization > Decimal("0.85"):
        return "attention"
    return "on_track"


def build_execution_charts(
    project: Project,
    financing: ProjectFinancing,
    cost_items: list[CostItem],
) -> dict:
    spent, capex, opex = summarize_project_spend(cost_items)
    investment = Decimal(str(project.investment_amount or 0))
    approved = financing.approved_amount
    disbursed = financing.disbursed_amount
    remaining_budget = investment - spent
    remaining_credit = approved - spent if approved > spent else Decimal("0")
    utilization_pct = float((spent / approved * 100) if approved > 0 else 0)

    monthly: dict[str, Decimal] = {}
    for item in cost_items:
        key = item.created_at.strftime("%Y-%m")
        monthly[key] = monthly.get(key, Decimal("0")) + Decimal(str(item.total_amount or 0))
    trend_keys = sorted(monthly.keys())[-6:]
    spend_trend = [{"month": k, "amount": float(monthly[k])} for k in trend_keys]

    capex_f = float(capex)
    opex_f = float(opex)
    spent_f = float(spent)
    remaining_f = max(float(remaining_budget), 0)

    return {
        "utilization_pct": round(utilization_pct, 1),
        "execution_pct_of_investment": round(
            float((spent / investment * 100) if investment > 0 else 0), 1
        ),
        "summary": {
            "approved_amount": float(approved),
            "disbursed_amount": float(disbursed),
            "investment_amount": float(investment),
            "spent_total": spent_f,
            "remaining_budget": float(remaining_budget),
            "currency": financing.currency,
        },
        "donut_execution": [
            {"label": "CAPEX", "value": capex_f, "color": "#00777f"},
            {"label": "OPEX", "value": opex_f, "color": "#fb923c"},
            {"label": "Saldo", "value": remaining_f, "color": "#34d399"},
        ],
        "bar_comparison": [
            {"label": "Aprovado", "value": float(approved), "color": "#011636"},
            {"label": "Desembolsado", "value": float(disbursed), "color": "#6366f1"},
            {"label": "Executado", "value": spent_f, "color": "#00777f"},
        ],
        "gauge": {
            "value": round(utilization_pct, 1),
            "max": 100,
            "label_pt": "Utilização do crédito",
            "label_en": "Credit utilization",
        },
        "spend_trend": spend_trend,
    }
