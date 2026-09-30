from decimal import Decimal
from uuid import UUID

from app.application.dto.report_data import ReportDataBundle, ReportProjectData
from app.domain.enums.cost_item_type import CostItemType
from app.domain.enums.report_language import ReportLanguage
from app.domain.repositories.analysis_repository import (
    IFinancialAnalysisRepository,
    IMonteCarloRepository,
    ISectorBenchmarkRepository,
    ISensitivityRepository,
)
from app.domain.repositories.audit_trail_repository import IAuditTrailRepository
from app.domain.repositories.budget_repository import IBudgetRepository
from app.domain.repositories.collaboration_repository import IKanbanTaskRepository
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.user_repository import IUserRepository


from app.application.services.fx_service import fx_rate


class ReportDataAggregator:
    """Agrega todos os dados do projeto para relatórios institucionais."""

    def __init__(
        self,
        project_repository: IProjectRepository,
        user_repository: IUserRepository,
        cost_item_repository: ICostItemRepository,
        budget_repository: IBudgetRepository,
        analysis_repository: IFinancialAnalysisRepository,
        monte_carlo_repository: IMonteCarloRepository,
        sensitivity_repository: ISensitivityRepository,
        benchmark_repository: ISectorBenchmarkRepository,
        audit_trail_repository: IAuditTrailRepository,
        task_repository: IKanbanTaskRepository,
    ) -> None:
        self._projects = project_repository
        self._users = user_repository
        self._items = cost_item_repository
        self._budgets = budget_repository
        self._analysis = analysis_repository
        self._monte_carlo = monte_carlo_repository
        self._sensitivity = sensitivity_repository
        self._benchmarks = benchmark_repository
        self._audit = audit_trail_repository
        self._tasks = task_repository

    def aggregate(
        self,
        project_id: UUID,
        *,
        report_currency: str = "AOA",
        report_language: str = "pt",
    ) -> ReportDataBundle:
        project = self._projects.find_by_id(project_id)
        if project is None:
            raise ValueError("Projeto não encontrado")

        owner = self._users.find_by_id(project.owner_id)
        items = self._items.find_by_project(project_id)
        capex = sum(i.total_amount for i in items if i.item_type == CostItemType.CAPEX)
        opex = sum(i.total_amount for i in items if i.item_type == CostItemType.OPEX)

        fx = self._fx_rate(project.currency.value, report_currency)

        bundle = ReportDataBundle(
            project=ReportProjectData(
                id=project.id,
                name=project.name,
                description=project.description,
                company_name=project.company_name,
                company_tax_id=project.company_tax_id,
                sector=project.sector.value,
                country=project.country.value,
                currency=project.currency.value,
                investment_amount=project.investment_amount,
                horizon_years=project.project_horizon_years,
                discount_rate=project.discount_rate,
                status=project.status.value,
                owner_name=owner.full_name if owner else None,
            ),
            cost_items=[
                {
                    "type": i.item_type.value,
                    "category": i.category,
                    "description": i.description,
                    "quantity": str(i.quantity),
                    "unit": i.unit,
                    "unit_price": str(i.unit_price),
                    "total": str(i.total_amount),
                    "hash": i.data_hash,
                    "supplier": i.supplier_name,
                }
                for i in items
            ],
            capex_total=capex,
            opex_total=opex,
            report_currency=report_currency,
            report_language=report_language,
            exchange_rate=fx,
        )

        bundle.budgets = [
            {
                "number": b.budget_number,
                "title": b.title,
                "total": str(b.total_amount),
                "status": b.status.value,
                "hash": b.verification_hash,
                "created_at": b.created_at.isoformat(),
            }
            for b in self._budgets.find_by_project(project_id)
        ]

        analyses = self._analysis.find_by_project(project_id, limit=1)
        if analyses:
            a = analyses[0]
            bundle.latest_analysis = {
                "id": str(a.id),
                "indicators_count": a.indicators_count,
                "hash": a.calculation_hash,
                "created_at": a.created_at.isoformat(),
            }
            bundle.indicators = a.indicators.get("items", [])
            bundle.indicators_summary = a.indicators.get("summary", {})
            bundle.cash_flows = a.cash_flows

        mc_runs = self._monte_carlo.find_by_project(project_id, limit=1)
        if mc_runs:
            mc = mc_runs[0]
            bundle.monte_carlo = {
                "iterations": mc.iterations,
                "parameters": mc.parameters,
                "results": mc.results,
                "created_at": mc.created_at.isoformat(),
            }

        sens_runs = self._sensitivity.find_by_project(project_id, limit=1)
        if sens_runs:
            sa = sens_runs[0]
            bundle.sensitivity = {
                "variables": sa.variables,
                "results": sa.results,
                "created_at": sa.created_at.isoformat(),
            }

        benchmarks = self._benchmarks.find_by_sector(project.sector.value)
        bundle.benchmarks = [
            {
                "key": b.metric_key,
                "label": b.metric_label,
                "value": b.average_value,
                "unit": b.unit,
            }
            for b in benchmarks
        ]

        bundle.audit_trail_count = self._audit.count_by_project(project_id)
        trail = self._audit.find_by_project(project_id, limit=15)
        bundle.audit_trail_sample = [
            {
                "action": e.action.value,
                "entity": e.entity_type.value,
                "hash": e.data_hash,
                "at": e.created_at.isoformat(),
            }
            for e in trail
        ]

        tasks = self._tasks.find_by_project(project_id)
        bundle.tasks_summary = {
            "total": len(tasks),
            "todo": sum(1 for t in tasks if t.status.value == "todo"),
            "in_progress": sum(1 for t in tasks if t.status.value == "in_progress"),
            "done": sum(1 for t in tasks if t.status.value == "done"),
        }

        return bundle

    def _fx_rate(self, from_ccy: str, to_ccy: str) -> float:
        return fx_rate(from_ccy, to_ccy)

    @staticmethod
    def format_money(amount: Decimal | float, currency: str, language: str) -> str:
        val = float(amount)
        if language == ReportLanguage.EN.value:
            return f"{currency} {val:,.2f}"
        return f"{val:,.2f} {currency}"
