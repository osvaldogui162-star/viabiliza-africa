from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from app.domain.entities.collaboration import KanbanTask
from app.domain.entities.project import Project
from app.domain.entities.project_financing import ProjectFinancing
from app.application.use_cases.projects.project_mapper import summarize_project_spend
from app.domain.entities.cost_item import CostItem
from app.application.services.financing_monitoring import compute_monitoring_status


def physical_progress_pct(tasks: list[KanbanTask]) -> float:
    if not tasks:
        return 0.0
    done = sum(1 for t in tasks if t.status.value == "done")
    return round(done / len(tasks) * 100, 1)


def schedule_status(tasks: list[KanbanTask], *, project_updated_at: datetime) -> str:
    today = date.today()
    overdue = [
        t
        for t in tasks
        if t.due_date and t.due_date < today and t.status.value != "done"
    ]
    if overdue:
        return "delayed"
    if tasks:
        return "on_time"
    days_idle = (datetime.now(timezone.utc) - project_updated_at.replace(tzinfo=timezone.utc)).days
    if days_idle > 30:
        return "stalled"
    return "unknown"


def build_financial_snapshot(
    *,
    project: Project,
    financing: ProjectFinancing,
    cost_items: list[CostItem],
) -> dict:
    spent, _, _ = summarize_project_spend(cost_items)
    approved = financing.approved_amount
    disbursed = financing.disbursed_amount
    investment = Decimal(str(project.investment_amount or 0))
    utilization = float((spent / approved * 100) if approved > 0 else 0)
    disbursement_gap = float(disbursed - spent) if disbursed > spent else 0.0
    budget_deviation_pct = float(
        ((spent - investment) / investment * 100) if investment > 0 else 0
    )
    return {
        "spent_total": str(spent.quantize(Decimal("0.01"))),
        "utilization_pct": round(utilization, 1),
        "disbursement_gap": round(disbursement_gap, 2),
        "budget_deviation_pct": round(budget_deviation_pct, 1),
        "execution_pct_of_investment": round(
            float((spent / investment * 100) if investment > 0 else 0), 1
        ),
    }


def build_schedule_snapshot(tasks: list[KanbanTask]) -> dict:
    today = date.today()
    upcoming = sorted(
        [t for t in tasks if t.due_date and t.status.value != "done"],
        key=lambda t: t.due_date or today,
    )[:5]
    return {
        "tasks_total": len(tasks),
        "tasks_done": sum(1 for t in tasks if t.status.value == "done"),
        "tasks_overdue": sum(
            1
            for t in tasks
            if t.due_date and t.due_date < today and t.status.value != "done"
        ),
        "milestones": [
            {
                "id": str(t.id),
                "title": t.title,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "status": t.status.value,
            }
            for t in upcoming
        ],
    }


def detect_project_alerts(
    *,
    project: Project,
    financing: ProjectFinancing,
    cost_items: list[CostItem],
    tasks: list[KanbanTask],
    pending_disbursements: int,
    pending_documents: int,
    pending_measurements: int,
) -> list[dict]:
    spent, _, _ = summarize_project_spend(cost_items)
    approved = financing.approved_amount
    disbursed = financing.disbursed_amount
    investment = Decimal(str(project.investment_amount or 0))
    alerts: list[dict] = []
    today = date.today()

    for t in tasks:
        if t.due_date and t.due_date < today and t.status.value != "done":
            alerts.append(
                {
                    "type": "delay",
                    "severity": "high",
                    "code": "task_overdue",
                    "message_pt": f"Tarefa em atraso: {t.title}",
                }
            )
            break

    if spent > investment and investment > 0:
        alerts.append(
            {
                "type": "financial_deviation",
                "severity": "critical",
                "code": "over_investment",
                "message_pt": "Execução financeira acima do investimento previsto.",
            }
        )
    elif approved > 0 and spent / approved > Decimal("0.95"):
        alerts.append(
            {
                "type": "financial_deviation",
                "severity": "medium",
                "code": "credit_near_limit",
                "message_pt": "Utilização do crédito aproxima-se do limite aprovado.",
            }
        )

    phys = physical_progress_pct(tasks)
    fin_exec = float((spent / investment * 100) if investment > 0 else 0)
    if investment > 0 and phys + 15 < fin_exec:
        alerts.append(
            {
                "type": "low_execution",
                "severity": "medium",
                "code": "physical_lag",
                "message_pt": "Execução física abaixo da execução financeira.",
            }
        )

    if pending_documents > 0:
        alerts.append(
            {
                "type": "missing_document",
                "severity": "medium",
                "code": "doc_pending_validation",
                "message_pt": f"{pending_documents} documento(s) aguardam validação.",
            }
        )

    if pending_disbursements > 0:
        alerts.append(
            {
                "type": "disbursement_pending",
                "severity": "high",
                "code": "disbursement_queue",
                "message_pt": f"{pending_disbursements} pedido(s) de desembolso pendente(s).",
            }
        )

    if pending_measurements > 0:
        alerts.append(
            {
                "type": "measurement_pending",
                "severity": "medium",
                "code": "measurement_pending",
                "message_pt": f"{pending_measurements} medição(ões) por registar.",
            }
        )

    if disbursed > spent + Decimal("1000") and approved > 0:
        alerts.append(
            {
                "type": "disbursement_pending",
                "severity": "low",
                "code": "undrawn_balance",
                "message_pt": "Saldo desembolsado não reflectido na execução.",
            }
        )

    sched = schedule_status(tasks, project_updated_at=project.updated_at)
    if sched == "stalled":
        alerts.append(
            {
                "type": "project_stalled",
                "severity": "high",
                "code": "no_activity",
                "message_pt": "Projecto sem actualização relevante há mais de 30 dias.",
            }
        )

    status = compute_monitoring_status(
        approved_amount=approved,
        spent_total=spent,
        investment_amount=investment,
    )
    if status == "critical":
        alerts.append(
            {
                "type": "financial_deviation",
                "severity": "critical",
                "code": "monitoring_critical",
                "message_pt": "Indicador de risco crítico na monitorização.",
            }
        )

    return alerts
