from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from app.application.services.financier_portfolio_loader import FinancierPortfolioLoader
from app.application.services.financier_project_snapshot import (
    build_financial_snapshot,
    build_schedule_snapshot,
    detect_project_alerts,
    physical_progress_pct,
    schedule_status,
)
from app.application.services.financier_serializers import bank_meta, financing_output
from app.application.services.financier_access_policy import FinancierAccessPolicy
from app.application.services.financing_monitoring import build_execution_charts, compute_monitoring_status
from app.application.services.terminal_monitoring_service import build_terminal_panel
from app.domain.repositories.analysis_repository import IFinancialAnalysisRepository
from app.domain.repositories.billing_integration_repository import IProjectBillingIntegrationRepository
from app.application.use_cases.projects.project_mapper import summarize_project_spend
from app.domain.exceptions.domain_exceptions import (
    AuthorizationError,
    EntityNotFoundError,
    ValidationError,
)
from app.domain.repositories.collaboration_repository import IKanbanTaskRepository
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.domain.repositories.financing_portal_repository import (
    IFinancingActivityRepository,
    IFinancingDisbursementRepository,
    IFinancingDocumentRepository,
)
from app.domain.repositories.project_financing_repository import IProjectFinancingRepository
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.user_repository import IUserRepository


def _activity_row(a) -> dict:
    return {
        "id": str(a.id),
        "action": a.action,
        "summary": a.summary,
        "actor_name": a.actor_name,
        "project_id": str(a.project_id) if a.project_id else None,
        "financing_id": str(a.financing_id) if a.financing_id else None,
        "created_at": a.created_at.isoformat(),
        "metadata": a.metadata,
    }


def _disbursement_row(d) -> dict:
    return {
        "id": str(d.id),
        "financing_id": str(d.financing_id),
        "requested_amount": str(d.requested_amount),
        "approved_amount": str(d.approved_amount) if d.approved_amount is not None else None,
        "paid_amount": str(d.paid_amount),
        "currency": d.currency,
        "status": d.status,
        "purpose": d.purpose,
        "requested_at": d.requested_at.isoformat(),
        "decided_at": d.decided_at.isoformat() if d.decided_at else None,
        "paid_at": d.paid_at.isoformat() if d.paid_at else None,
        "notes": d.notes,
    }


def _document_row(doc) -> dict:
    return {
        "id": str(doc.id),
        "financing_id": str(doc.financing_id),
        "doc_type": doc.doc_type,
        "title": doc.title,
        "file_ref": doc.file_ref,
        "validation_status": doc.validation_status,
        "created_at": doc.created_at.isoformat(),
        "notes": doc.notes,
    }


class GetFinancierDashboardUseCase:
    def __init__(self, loader: FinancierPortfolioLoader, activity: IFinancingActivityRepository) -> None:
        self._loader = loader
        self._activity = activity

    def execute(self, *, actor_id: UUID) -> dict:
        actor, visible, bank_filter = self._loader.load_visible_financings(actor_id)
        items = []
        stats = {"on_track": 0, "attention": 0, "critical": 0}
        total_exposure = Decimal("0")
        total_disbursed = Decimal("0")
        total_executed = Decimal("0")
        all_alerts: list[dict] = []

        for f in visible:
            project = self._loader._projects.find_by_id(f.project_id)
            if project is None:
                continue
            row = self._loader.enrich_item(f, project)
            items.append(row)
            stats[row["monitoring_status"]] = stats.get(row["monitoring_status"], 0) + 1
            total_exposure += f.approved_amount
            total_disbursed += f.disbursed_amount
            total_executed += Decimal(str(row["spent_total"]))
            for al in row.get("alerts_preview") or []:
                all_alerts.append(
                    {
                        **al,
                        "financing_id": row["id"],
                        "project_id": row["project_id"],
                        "project_name": row["project_name"],
                    }
                )

        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        all_alerts.sort(key=lambda a: severity_order.get(a.get("severity", "low"), 9))

        pending_items = [a for a in all_alerts if a.get("severity") in ("critical", "high", "medium")][:20]

        pending_approvals: list[dict] = []
        if actor.role.value in ("admin", "bank"):
            if actor.role.value == "admin":
                pending_rows = self._loader._financing.list_all_pending()
            elif bank_filter:
                pending_rows = self._loader._financing.list_pending_by_bank(bank_filter)
            else:
                pending_rows = []
            for f in pending_rows:
                project = self._loader._projects.find_by_id(f.project_id)
                if project is None:
                    continue
                pending_approvals.append(
                    financing_output(
                        f,
                        project_name=project.name,
                        company_name=project.company_name,
                        sector=project.sector.value,
                    )
                )

        recent_activity: list[dict] = []
        if bank_filter:
            recent_activity = [_activity_row(a) for a in self._activity.list_by_bank(bank_filter, limit=15)]

        exec_pct = float(
            (total_executed / total_exposure * 100) if total_exposure > 0 else 0
        )
        disb_pct = float(
            (total_disbursed / total_exposure * 100) if total_exposure > 0 else 0
        )

        monthly: dict[str, Decimal] = {}
        for f in visible:
            for cost in self._loader._cost_items.find_by_project(f.project_id):
                key = cost.created_at.strftime("%Y-%m")
                monthly[key] = monthly.get(key, Decimal("0")) + Decimal(
                    str(cost.total_amount or 0)
                )
        trend_keys = sorted(monthly.keys())[-6:]
        spend_trend = [{"month": k, "amount": float(monthly[k])} for k in trend_keys]

        top_projects = sorted(
            items,
            key=lambda x: float(x.get("approved_amount") or 0),
            reverse=True,
        )[:6]
        project_comparison = [
            {
                "financing_id": p["id"],
                "name": p["project_name"],
                "financial_pct": float(p.get("utilization_pct") or 0),
                "physical_pct": float(p.get("physical_pct") or 0),
                "approved": p["approved_amount"],
            }
            for p in top_projects
        ]

        avg_util = (
            sum(float(i.get("utilization_pct") or 0) for i in items) / len(items)
            if items
            else 0.0
        )

        charts = {
            "bar_comparison": [
                {"label": "Aprovado", "value": float(total_exposure), "color": "#011636"},
                {"label": "Desembolsado", "value": float(total_disbursed), "color": "#6366f1"},
                {"label": "Executado", "value": float(total_executed), "color": "#2dd4bf"},
            ],
            "risk_donut": [
                {"label": "Em linha", "value": float(stats.get("on_track", 0)), "color": "#34d399"},
                {"label": "Atenção", "value": float(stats.get("attention", 0)), "color": "#fbbf24"},
                {"label": "Crítico", "value": float(stats.get("critical", 0)), "color": "#f87171"},
            ],
            "spend_trend": spend_trend,
            "project_comparison": project_comparison,
            "gauge": {
                "value": round(avg_util, 1),
                "max": 100,
                "label_pt": "Utilização média da carteira",
                "label_en": "Portfolio avg. utilization",
            },
            "physical_vs_financial": {
                "avg_financial_pct": round(exec_pct, 1),
                "avg_physical_pct": round(
                    sum(i.get("physical_pct", 0) for i in items) / len(items), 1
                )
                if items
                else 0,
            },
        }

        billing_connected = sum(1 for i in items if i.get("billing_connected"))
        deviations = [float(i["deviation_pct"]) for i in items if i.get("deviation_pct") is not None]
        avg_deviation = round(sum(deviations) / len(deviations), 1) if deviations else None
        risk_mix = {"low": 0, "medium": 0, "high": 0}
        for i in items:
            lvl = i.get("risk_level")
            if lvl in risk_mix:
                risk_mix[lvl] += 1

        return {
            "sections": {
                "carteira": {
                    "projects_count": len(items),
                    "total_exposure": str(total_exposure),
                    "currency": items[0]["currency"] if items else "AOA",
                },
                "terminal": {
                    "billing_connected_count": billing_connected,
                    "billing_required_count": len(items) - billing_connected,
                    "avg_deviation_pct": avg_deviation,
                    "risk_mix": risk_mix,
                },
                "exposicao": {
                    "total_approved": str(total_exposure),
                    "by_risk": stats,
                },
                "desembolsos": {
                    "total_disbursed": str(total_disbursed),
                    "disbursement_vs_approved_pct": round(disb_pct, 1),
                    "pending_requests": sum(
                        self._loader._disbursements.count_pending_by_financing(UUID(i["id"]))
                        for i in items
                    ),
                },
                "execucao": {
                    "total_executed": str(total_executed.quantize(Decimal("0.01"))),
                    "execution_vs_approved_pct": round(exec_pct, 1),
                    "avg_physical_pct": round(
                        sum(i.get("physical_pct", 0) for i in items) / len(items), 1
                    )
                    if items
                    else 0,
                },
                "risco": stats,
                "pendencias": {
                    "alerts_count": len(all_alerts),
                    "top": pending_items[:8],
                },
                "aprovacoes_pendentes": {
                    "count": len(pending_approvals),
                    "items": pending_approvals[:8],
                },
            },
            "pending_approvals": pending_approvals,
            "items": items,
            "total": len(items),
            "stats": {
                **stats,
                "total_exposure": str(total_exposure),
            },
            "viewer_bank": bank_meta(bank_filter) if bank_filter else None,
            "recent_activity": recent_activity,
            "charts": charts,
        }


class ListFinancierAlertsUseCase:
    def __init__(self, loader: FinancierPortfolioLoader) -> None:
        self._loader = loader

    def execute(self, *, actor_id: UUID) -> dict:
        actor, visible, _ = self._loader.load_visible_financings(actor_id)
        if actor is None or not self._loader._policy.can_list_portfolio(actor):
            raise AuthorizationError("Sem acesso")

        alerts: list[dict] = []
        for f in visible:
            project = self._loader._projects.find_by_id(f.project_id)
            if project is None:
                continue
            row = self._loader.enrich_item(f, project)
            cost_items = self._loader._cost_items.find_by_project(f.project_id)
            tasks = self._loader._tasks.find_by_project(f.project_id)
            pending_disb = self._loader._disbursements.count_pending_by_financing(f.id)
            pending_docs = self._loader._documents.count_pending_by_financing(f.id)
            pending_meas = sum(
                1
                for d in self._loader._documents.list_by_financing(f.id)
                if d.doc_type == "measurement" and d.validation_status == "pending"
            )
            for al in detect_project_alerts(
                project=project,
                financing=f,
                cost_items=cost_items,
                tasks=tasks,
                pending_disbursements=pending_disb,
                pending_documents=pending_docs,
                pending_measurements=pending_meas,
            ):
                alerts.append(
                    {
                        **al,
                        "financing_id": str(f.id),
                        "project_id": str(project.id),
                        "project_name": project.name,
                    }
                )
            if self._loader._analysis is not None and self._loader._billing is not None:
                analyses = self._loader._analysis.find_by_project(f.project_id, limit=1)
                integration = self._loader._billing.find_by_project(f.project_id)
                terminal = build_terminal_panel(
                    project=project,
                    analysis=analyses[0] if analyses else None,
                    integration=integration,
                    physical_pct=physical_progress_pct(tasks),
                )
                for al in terminal.get("alerts") or []:
                    alerts.append(
                        {
                            **al,
                            "financing_id": str(f.id),
                            "project_id": str(project.id),
                            "project_name": project.name,
                        }
                    )
        return {"items": alerts, "total": len(alerts)}


class GetFinancierProjectDetailUseCase:
    """Detalhe completo do projecto financiado (monitorização + operações)."""

    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        financing_repo: IProjectFinancingRepository,
        cost_items: ICostItemRepository,
        tasks: IKanbanTaskRepository,
        disbursements: IFinancingDisbursementRepository,
        documents: IFinancingDocumentRepository,
        activity: IFinancingActivityRepository,
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
        self._activity = activity
        self._policy = policy
        self._analysis = analysis
        self._billing = billing

    def execute(self, *, actor_id: UUID, financing_id: UUID) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        financing = self._financing.find_by_id(financing_id)
        if financing is None or not financing.is_active:
            raise EntityNotFoundError("Financiamento", str(financing_id))
        project = self._projects.find_by_id(financing.project_id)
        if project is None:
            raise EntityNotFoundError("Projeto", str(financing.project_id))
        if not self._policy.can_view_financing(actor, financing, project=project):
            raise AuthorizationError("Sem acesso a este financiamento")

        if financing.is_pending_bank():
            return {
                "financing": financing_output(
                    financing,
                    project_name=project.name,
                    company_name=project.company_name,
                    sector=project.sector.value,
                ),
                "project": {
                    "id": str(project.id),
                    "name": project.name,
                    "company_name": project.company_name,
                    "sector_label": project.sector.label_pt,
                    "status": project.status.value,
                    "province": project.company_province,
                    "updated_at": project.updated_at.isoformat(),
                    "investment_amount": str(project.investment_amount),
                },
                "monitoring_status": financing.monitoring_status,
                "workflow": {
                    "status": financing.workflow_status,
                    "awaiting_bank_decision": True,
                    "can_decide": self._policy.can_decide_financing(actor, financing),
                },
                "charts": None,
                "alerts": [],
                "disbursements": [],
                "documents": [],
                "activity": [
                    _activity_row(a)
                    for a in self._activity.list_by_financing(financing.id, limit=40)
                ],
            }

        items = self._cost_items.find_by_project(project.id)
        task_list = self._tasks.find_by_project(project.id)
        spent, _, _ = summarize_project_spend(items)
        status = compute_monitoring_status(
            approved_amount=financing.approved_amount,
            spent_total=spent,
            investment_amount=Decimal(str(project.investment_amount or 0)),
        )
        if status != financing.monitoring_status:
            financing = self._financing.update_monitoring_status(financing.id, status)

        charts = build_execution_charts(project, financing, items)
        pending_disb = self._disbursements.count_pending_by_financing(financing.id)
        pending_docs = self._documents.count_pending_by_financing(financing.id)
        pending_meas = sum(
            1
            for d in self._documents.list_by_financing(financing.id)
            if d.doc_type == "measurement" and d.validation_status == "pending"
        )
        alerts = detect_project_alerts(
            project=project,
            financing=financing,
            cost_items=items,
            tasks=task_list,
            pending_disbursements=pending_disb,
            pending_documents=pending_docs,
            pending_measurements=pending_meas,
        )

        terminal = None
        if self._analysis is not None and self._billing is not None:
            analyses = self._analysis.find_by_project(project.id, limit=1)
            integration = self._billing.find_by_project(project.id)
            terminal = build_terminal_panel(
                project=project,
                analysis=analyses[0] if analyses else None,
                integration=integration,
                physical_pct=physical_progress_pct(task_list),
            )
            alerts = list(alerts) + list(terminal.get("alerts") or [])

        return {
            "financing": financing_output(
                financing,
                project_name=project.name,
                company_name=project.company_name,
                sector=project.sector.value,
            ),
            "project": {
                "id": str(project.id),
                "name": project.name,
                "company_name": project.company_name,
                "sector_label": project.sector.label_pt,
                "status": project.status.value,
                "province": project.company_province,
                "updated_at": project.updated_at.isoformat(),
                "investment_amount": str(project.investment_amount),
            },
            "monitoring_status": status,
            "charts": charts,
            "financial": build_financial_snapshot(
                project=project, financing=financing, cost_items=items
            ),
            "physical": {
                "progress_pct": physical_progress_pct(task_list),
                "tasks_summary": build_schedule_snapshot(task_list),
            },
            "schedule": {
                "status": schedule_status(task_list, project_updated_at=project.updated_at),
                "milestones": build_schedule_snapshot(task_list)["milestones"],
            },
            "alerts": alerts,
            "disbursements": [
                _disbursement_row(d) for d in self._disbursements.list_by_financing(financing.id)
            ],
            "documents": [
                _document_row(d) for d in self._documents.list_by_financing(financing.id)
            ],
            "activity": [
                _activity_row(a)
                for a in self._activity.list_by_financing(financing.id, limit=40)
            ],
            "workflow": {
                "status": financing.workflow_status,
                "awaiting_bank_decision": False,
                "can_decide": False,
            },
            "terminal": terminal,
        }


class ListFinancierDisbursementsUseCase:
    def __init__(
        self,
        loader: FinancierPortfolioLoader,
        disbursements: IFinancingDisbursementRepository,
        projects: IProjectRepository,
        financing_repo: IProjectFinancingRepository,
    ) -> None:
        self._loader = loader
        self._disbursements = disbursements
        self._projects = projects
        self._financing = financing_repo

    def execute(self, *, actor_id: UUID) -> dict:
        actor, visible, _ = self._loader.load_visible_financings(actor_id)
        if not self._loader._policy.can_list_portfolio(actor):
            raise AuthorizationError("Sem acesso")
        ids = [f.id for f in visible]
        rows = self._disbursements.list_by_financing_ids(ids)
        out = []
        fin_by_id = {f.id: f for f in visible}
        for d in rows:
            f = fin_by_id.get(d.financing_id)
            if not f:
                continue
            project = self._projects.find_by_id(f.project_id)
            out.append(
                {
                    **_disbursement_row(d),
                    "project_id": str(f.project_id),
                    "project_name": project.name if project else "—",
                }
            )
        return {"items": out, "total": len(out)}


class CreateFinancingDisbursementUseCase:
    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        financing_repo: IProjectFinancingRepository,
        disbursements: IFinancingDisbursementRepository,
        activity: IFinancingActivityRepository,
        policy: FinancierAccessPolicy,
    ) -> None:
        self._users = users
        self._projects = projects
        self._financing = financing_repo
        self._disbursements = disbursements
        self._activity = activity
        self._policy = policy

    def execute(
        self,
        *,
        actor_id: UUID,
        financing_id: UUID,
        requested_amount: Decimal,
        purpose: str | None,
    ) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        financing = self._financing.find_by_id(financing_id)
        if financing is None:
            raise EntityNotFoundError("Financiamento", str(financing_id))
        project = self._projects.find_by_id(financing.project_id)
        if project is None:
            raise EntityNotFoundError("Projeto", str(financing.project_id))
        if not self._policy.can_operate_financing(actor, financing, project=project):
            raise AuthorizationError("Sem permissão ou financiamento ainda não activo")
        if requested_amount <= 0:
            raise ValidationError("Montante inválido")

        created = self._disbursements.create(
            financing_id=financing_id,
            requested_amount=requested_amount,
            currency=financing.currency,
            purpose=purpose,
            requested_by=actor_id,
        )
        self._activity.append(
            bank_code=financing.bank_code,
            action="disbursement_requested",
            summary=f"Pedido de desembolso: {requested_amount} {financing.currency}",
            financing_id=financing_id,
            project_id=project.id,
            actor_id=actor_id,
            actor_name=actor.full_name,
        )
        return _disbursement_row(created)


class UpdateFinancingDisbursementUseCase:
    VALID = ("under_review", "approved", "paid", "rejected")

    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        financing_repo: IProjectFinancingRepository,
        disbursements: IFinancingDisbursementRepository,
        activity: IFinancingActivityRepository,
        policy: FinancierAccessPolicy,
    ) -> None:
        self._users = users
        self._projects = projects
        self._financing = financing_repo
        self._disbursements = disbursements
        self._activity = activity
        self._policy = policy

    def execute(
        self,
        *,
        actor_id: UUID,
        disbursement_id: UUID,
        status: str,
        approved_amount: Decimal | None = None,
        notes: str | None = None,
    ) -> dict:
        if status not in self.VALID:
            raise ValidationError("Estado inválido")
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        if actor.role.value not in ("bank", "admin", "financial"):
            raise AuthorizationError("Sem permissão para actualizar desembolso")
        if status in ("approved", "paid", "rejected") and actor.role.value == "financial":
            raise AuthorizationError("Análise bancária reservada ao perfil instituição")

        row = self._disbursements.find_by_id(disbursement_id)
        if row is None:
            raise EntityNotFoundError("Desembolso", str(disbursement_id))
        financing = self._financing.find_by_id(row.financing_id)
        if financing is None:
            raise EntityNotFoundError("Financiamento", str(row.financing_id))
        project = self._projects.find_by_id(financing.project_id)
        if project is None or not self._policy.can_view_financing(actor, financing, project=project):
            raise AuthorizationError("Sem permissão")

        paid = None
        if status == "paid":
            paid = approved_amount or row.approved_amount or row.requested_amount
        updated = self._disbursements.update_status(
            disbursement_id,
            status=status,
            reviewed_by=actor_id,
            approved_amount=approved_amount,
            paid_amount=paid,
            notes=notes,
        )
        if status == "paid" and paid:
            new_disbursed = financing.disbursed_amount + paid
            self._financing.update_disbursed_amount(financing.id, new_disbursed)

        self._activity.append(
            bank_code=financing.bank_code,
            action=f"disbursement_{status}",
            summary=f"Desembolso {status}: {updated.requested_amount} {updated.currency}",
            financing_id=financing.id,
            project_id=project.id,
            actor_id=actor_id,
            actor_name=actor.full_name,
        )
        return _disbursement_row(updated)


class CreateFinancingDocumentUseCase:
    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        financing_repo: IProjectFinancingRepository,
        documents: IFinancingDocumentRepository,
        activity: IFinancingActivityRepository,
        policy: FinancierAccessPolicy,
    ) -> None:
        self._users = users
        self._projects = projects
        self._financing = financing_repo
        self._documents = documents
        self._activity = activity
        self._policy = policy

    def execute(
        self,
        *,
        actor_id: UUID,
        financing_id: UUID,
        doc_type: str,
        title: str,
        file_ref: str | None,
    ) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        financing = self._financing.find_by_id(financing_id)
        if financing is None:
            raise EntityNotFoundError("Financiamento", str(financing_id))
        project = self._projects.find_by_id(financing.project_id)
        if project is None or not self._policy.can_operate_financing(actor, financing, project=project):
            raise AuthorizationError("Sem permissão ou financiamento ainda não activo")
        if doc_type not in ("contract", "guarantee", "measurement", "report", "other"):
            raise ValidationError("Tipo de documento inválido")

        doc = self._documents.create(
            financing_id=financing_id,
            doc_type=doc_type,
            title=title.strip(),
            file_ref=file_ref,
            uploaded_by=actor_id,
        )
        self._activity.append(
            bank_code=financing.bank_code,
            action="document_uploaded",
            summary=f"Documento: {title}",
            financing_id=financing_id,
            project_id=project.id,
            actor_id=actor_id,
            actor_name=actor.full_name,
        )
        return _document_row(doc)


class ValidateFinancingDocumentUseCase:
    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        financing_repo: IProjectFinancingRepository,
        documents: IFinancingDocumentRepository,
        activity: IFinancingActivityRepository,
        policy: FinancierAccessPolicy,
    ) -> None:
        self._users = users
        self._projects = projects
        self._financing = financing_repo
        self._documents = documents
        self._activity = activity
        self._policy = policy

    def execute(
        self,
        *,
        actor_id: UUID,
        document_id: UUID,
        validation_status: str,
        notes: str | None = None,
    ) -> dict:
        if validation_status not in ("valid", "rejected"):
            raise ValidationError("Estado inválido")
        actor = self._users.find_by_id(actor_id)
        if actor is None or actor.role.value not in ("bank", "admin"):
            raise AuthorizationError("Apenas o banco valida documentos")

        doc = self._documents.find_by_id(document_id)
        if doc is None:
            raise EntityNotFoundError("Documento", str(document_id))
        financing = self._financing.find_by_id(doc.financing_id)
        if financing is None:
            raise EntityNotFoundError("Financiamento", str(doc.financing_id))
        project = self._projects.find_by_id(financing.project_id)
        if project is None or not self._policy.can_view_financing(actor, financing, project=project):
            raise AuthorizationError("Sem permissão")

        updated = self._documents.update_validation(
            document_id,
            validation_status=validation_status,
            validated_by=actor_id,
            notes=notes,
        )
        self._activity.append(
            bank_code=financing.bank_code,
            action=f"document_{validation_status}",
            summary=f"Documento {validation_status}: {doc.title}",
            financing_id=financing.id,
            project_id=project.id,
            actor_id=actor_id,
            actor_name=actor.full_name,
        )
        return _document_row(updated)


class ListFinancierDocumentsUseCase:
    def __init__(
        self,
        loader: FinancierPortfolioLoader,
        documents: IFinancingDocumentRepository,
        projects: IProjectRepository,
    ) -> None:
        self._loader = loader
        self._documents = documents
        self._projects = projects

    def execute(self, *, actor_id: UUID) -> dict:
        actor, visible, _ = self._loader.load_visible_financings(actor_id)
        if actor is None or not self._loader._policy.can_list_portfolio(actor):
            raise AuthorizationError("Sem acesso")
        ids = [f.id for f in visible]
        rows = self._documents.list_by_financing_ids(ids)
        fin_by_id = {f.id: f for f in visible}
        out = []
        for d in rows:
            f = fin_by_id.get(d.financing_id)
            if not f:
                continue
            project = self._projects.find_by_id(f.project_id)
            out.append(
                {
                    **_document_row(d),
                    "project_id": str(f.project_id),
                    "project_name": project.name if project else "—",
                }
            )
        return {"items": out, "total": len(out)}


class ListFinancierActivityUseCase:
    def __init__(
        self,
        loader: FinancierPortfolioLoader,
        activity: IFinancingActivityRepository,
    ) -> None:
        self._loader = loader
        self._activity = activity

    def execute(self, *, actor_id: UUID, limit: int = 50) -> dict:
        actor, _, bank_filter = self._loader.load_visible_financings(actor_id)
        if actor is None or not self._loader._policy.can_list_portfolio(actor):
            raise AuthorizationError("Sem acesso")
        if bank_filter:
            items = [_activity_row(a) for a in self._activity.list_by_bank(bank_filter, limit=limit)]
        else:
            items = []
        return {"items": items, "total": len(items)}


class ExportFinancierPortfolioReportUseCase:
    def __init__(self, dashboard: GetFinancierDashboardUseCase) -> None:
        self._dashboard = dashboard

    def execute(self, *, actor_id: UUID) -> dict:
        data = self._dashboard.execute(actor_id=actor_id)
        rows = []
        for item in data["items"]:
            rows.append(
                {
                    "projecto": item["project_name"],
                    "empresa": item.get("company_name"),
                    "aprovado": item["approved_amount"],
                    "desembolsado": item["disbursed_amount"],
                    "executado": item.get("spent_total"),
                    "fisico_pct": item.get("physical_pct"),
                    "risco": item["monitoring_status"],
                    "pendencias": item.get("pending_count"),
                }
            )
        from datetime import datetime, timezone

        return {
            "format": "json",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "rows": rows,
            "summary": data["sections"],
        }
