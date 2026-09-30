"""Validação de pré-requisitos antes de gerar relatórios (UC01–UC03)."""

from __future__ import annotations

from uuid import UUID

from app.domain.enums.budget_status import BudgetStatus
from app.domain.enums.report_type import ReportType
from app.domain.exceptions.domain_exceptions import ValidationError
from app.domain.repositories.analysis_repository import IFinancialAnalysisRepository, IMonteCarloRepository
from app.domain.repositories.budget_repository import IBudgetRepository
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.domain.repositories.project_repository import IProjectRepository


class ReportPrerequisitesValidator:
    def __init__(
        self,
        project_repository: IProjectRepository,
        cost_item_repository: ICostItemRepository,
        budget_repository: IBudgetRepository,
        analysis_repository: IFinancialAnalysisRepository,
        monte_carlo_repository: IMonteCarloRepository,
    ) -> None:
        self._projects = project_repository
        self._items = cost_item_repository
        self._budgets = budget_repository
        self._analysis = analysis_repository
        self._monte_carlo = monte_carlo_repository

    def validate(
        self,
        project_id: UUID,
        report_type: ReportType,
        *,
        currency: str,
    ) -> None:
        pending = self.collect_pending(project_id, report_type, currency=currency)
        if pending:
            lines = "\n".join(f"• {item}" for item in pending)
            raise ValidationError(
                f"Dados em falta para gerar o relatório:\n{lines}"
            )

    def collect_pending(
        self,
        project_id: UUID,
        report_type: ReportType,
        *,
        currency: str,
    ) -> list[str]:
        project = self._projects.find_by_id(project_id)
        if project is None:
            return ["Projecto não encontrado"]

        pending: list[str] = []
        items = self._items.find_by_project(project_id)
        budgets = self._budgets.find_by_project(project_id)
        analyses = self._analysis.find_by_project(project_id, limit=1)
        mc_runs = self._monte_carlo.find_by_project(project_id, limit=1)

        has_approved = any(b.status == BudgetStatus.APPROVED for b in budgets)
        has_traceable = any(b.verification_hash for b in budgets)

        if report_type == ReportType.INTERNATIONAL:
            if not items:
                pending.append("Adicionar itens de custo (tab Ingestão)")
            if not analyses:
                pending.append("Calcular indicadores financeiros (tab Análise)")
            if not mc_runs:
                pending.append("Executar simulação Monte Carlo (tab Análise)")
            if not has_traceable:
                pending.append("Gerar orçamento rastreável com QR Code (tab Ingestão)")

        elif report_type == ReportType.BFA:
            if not project.company_tax_id:
                pending.append("Preencher NIF da empresa (dados do projecto)")
            if not project.rep_id_number:
                pending.append("Anexar/preencher BI do representante legal")
            if not project.company_name:
                pending.append("Preencher nome da empresa")
            if currency != "AOA" and project.currency.value != "AOA":
                pending.append("Relatório BFA requer valores em Kwanza (AOA)")
            if not analyses:
                pending.append("Calcular indicadores financeiros (tab Análise)")
            if not has_approved:
                pending.append("Aprovar orçamento antes de gerar relatório BFA")

        elif report_type == ReportType.BDA:
            if currency != "USD":
                pending.append("Formulário BDA requer moeda USD (ou conversão)")
            if not project.investment_amount or project.investment_amount <= 0:
                pending.append("Definir montante de investimento no projecto")
            if project.project_horizon_years < 1:
                pending.append("Definir horizonte do projecto (mín. 1 ano)")
            if not items:
                pending.append("Adicionar dados de investimento / itens de custo")

        return pending
