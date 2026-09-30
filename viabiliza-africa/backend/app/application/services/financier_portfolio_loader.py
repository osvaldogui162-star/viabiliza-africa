from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from app.application.services.financier_project_snapshot import (
    build_financial_snapshot,
    build_schedule_snapshot,
    detect_project_alerts,
    physical_progress_pct,
    schedule_status,
)
from app.application.services.financing_monitoring import compute_monitoring_status
from app.application.services.financier_serializers import financing_output as _financing_output
from app.application.services.financier_access_policy import FinancierAccessPolicy
from app.application.use_cases.projects.project_mapper import summarize_project_spend
from app.domain.entities.project import Project
from app.domain.entities.project_financing import ProjectFinancing
from app.domain.repositories.collaboration_repository import IKanbanTaskRepository
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.domain.repositories.financing_portal_repository import (
    IFinancingDisbursementRepository,
    IFinancingDocumentRepository,
)
from app.domain.repositories.project_financing_repository import IProjectFinancingRepository
from app.domain.repositories.project_repository import IProjectRepository, ProjectFilters
from app.domain.repositories.user_repository import IUserRepository
from app.domain.repositories.analysis_repository import IFinancialAnalysisRepository
from app.domain.repositories.billing_integration_repository import IProjectBillingIntegrationRepository
from app.application.services.terminal_monitoring_service import (
    build_terminal_panel,
    build_terminal_portfolio_fields,
)
from app.domain.exceptions.domain_exceptions import AuthorizationError, EntityNotFoundError


class FinancierPortfolioLoader:
    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        financing_repo: IProjectFinancingRepository,
        cost_items: ICostItemRepository,
        tasks: IKanbanTaskRepository,
        disbursements: IFinancingDisbursementRepository,
        documents: IFinancingDocumentRepository,
        policy: FinancierAccessPolicy,
        analysis: IFinancialAnalysisRepository | None = None,
        billing: IProjectBillingIntegrationRepository | None = None,
    ) -> None:
        self._users = users
        self._projects = projects
        self._financing = financing_repo
        self._cost_items = cost_items
        self._tasks = tasks
        self._disbursements = disbursements
        self._documents = documents
        self._policy = policy
        self._analysis = analysis
        self._billing = billing

    def load_visible_financings(self, actor_id: UUID) -> tuple[object, list[ProjectFinancing], str | None]:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        if not self._policy.can_list_portfolio(actor):
            raise AuthorizationError("Sem acesso ao portal do financiador")

        bank_filter = self._policy.portfolio_bank_code(actor)
        if actor.role.value == "admin":
            financings = self._financing.list_all_active()
        elif bank_filter:
            financings = self._financing.list_by_bank(bank_filter)
        else:
            financings = []
            owner_id = self._policy.financial_owner_id_filter(actor)
            if owner_id:
                owned = self._projects.find_all(
                    ProjectFilters(owner_id=owner_id), limit=200, offset=0
                )
                for p in owned:
                    financings.extend(self._financing.find_by_project(p.id))

        visible: list[ProjectFinancing] = []
        for f in financings:
            if not f.is_portfolio_active():
                continue
            project = self._projects.find_by_id(f.project_id)
            if project is None:
                continue
            if not self._policy.can_view_financing(actor, f, project=project):
                continue
            visible.append(f)
        return actor, visible, bank_filter

    def enrich_item(self, f: ProjectFinancing, project: Project) -> dict:
        if not f.is_portfolio_active():
            return {
                **_financing_output(
                    f,
                    project_name=project.name,
                    company_name=project.company_name,
                    sector=project.sector.value,
                ),
                "project_status": project.status.value,
            }

        cost_items = self._cost_items.find_by_project(f.project_id)
        tasks = self._tasks.find_by_project(f.project_id)
        spent, _, _ = summarize_project_spend(cost_items)
        status = compute_monitoring_status(
            approved_amount=f.approved_amount,
            spent_total=spent,
            investment_amount=Decimal(str(project.investment_amount or 0)),
        )
        if status != f.monitoring_status:
            f = self._financing.update_monitoring_status(f.id, status)

        pending_disb = self._disbursements.count_pending_by_financing(f.id)
        pending_docs = self._documents.count_pending_by_financing(f.id)
        pending_meas = sum(
            1
            for d in self._documents.list_by_financing(f.id)
            if d.doc_type == "measurement" and d.validation_status == "pending"
        )

        financial = build_financial_snapshot(
            project=project, financing=f, cost_items=cost_items
        )
        physical_pct = physical_progress_pct(tasks)
        sched = schedule_status(tasks, project_updated_at=project.updated_at)
        alerts = detect_project_alerts(
            project=project,
            financing=f,
            cost_items=cost_items,
            tasks=tasks,
            pending_disbursements=pending_disb,
            pending_documents=pending_docs,
            pending_measurements=pending_meas,
        )

        terminal_fields: dict = {}
        if self._analysis is not None and self._billing is not None:
            analyses = self._analysis.find_by_project(f.project_id, limit=1)
            integration = self._billing.find_by_project(f.project_id)
            terminal = build_terminal_panel(
                project=project,
                analysis=analyses[0] if analyses else None,
                integration=integration,
                physical_pct=physical_pct,
            )
            terminal_fields = build_terminal_portfolio_fields(terminal)
            for tal in terminal.get("alerts") or []:
                alerts.append(tal)

        return {
            **_financing_output(
                f,
                project_name=project.name,
                company_name=project.company_name,
                sector=project.sector.value,
            ),
            **financial,
            **terminal_fields,
            "project_status": project.status.value,
            "physical_pct": physical_pct,
            "schedule_status": sched,
            "schedule": build_schedule_snapshot(tasks),
            "pending_count": len(alerts),
            "alerts_preview": alerts[:3],
        }
