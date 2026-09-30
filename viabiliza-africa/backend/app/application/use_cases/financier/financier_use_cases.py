from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from app.application.services.financier_access_policy import FinancierAccessPolicy
from app.application.services.financier_serializers import bank_meta as _bank_meta, financing_output as _financing_output
from app.application.services.financing_monitoring import compute_monitoring_status
from app.application.use_cases.projects.project_mapper import summarize_project_spend
from app.domain.enums.financing_bank import FinancingBank
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.domain_exceptions import (
    AuthorizationError,
    EntityNotFoundError,
    ValidationError,
)
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.domain.repositories.financing_portal_repository import IFinancingActivityRepository
from app.domain.repositories.project_financing_repository import IProjectFinancingRepository
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.user_repository import IUserRepository


def _assert_no_conflicting_financing(financing_repo: IProjectFinancingRepository, project_id: UUID, bank_code: str) -> None:
    for row in financing_repo.find_by_project(project_id, active_only=True):
        if row.bank_code.lower() != bank_code:
            continue
        if row.is_pending_bank():
            raise ValidationError("Já existe um pedido de financiamento aguardando decisão deste banco.")
        if row.is_portfolio_active():
            raise ValidationError("Já existe financiamento activo com este banco para o projecto.")


class CreateProjectFinancingUseCase:
    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        financing_repo: IProjectFinancingRepository,
        cost_items: ICostItemRepository,
        policy: FinancierAccessPolicy,
        activity: IFinancingActivityRepository,
    ) -> None:
        self._users = users
        self._projects = projects
        self._financing = financing_repo
        self._cost_items = cost_items
        self._policy = policy
        self._activity = activity

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        bank_code: str,
        decision: str | None = None,
        approved_amount: Decimal,
        currency: str,
        disbursed_amount: Decimal | None = None,
        interest_rate_pct: Decimal | None = None,
        term_months: int | None = None,
        submission_id: UUID | None = None,
        notes: str | None = None,
    ) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        project = self._projects.find_by_id(project_id)
        if project is None:
            raise EntityNotFoundError("Projeto", str(project_id))
        if not self._policy.can_register_financing(actor, project):
            raise AuthorizationError("Sem permissão para registar financiamento")

        code = bank_code.strip().lower()
        if not FinancingBank.is_valid(code):
            raise ValidationError(
                f"Código de banco inválido. Use um banco do catálogo: {', '.join(FinancingBank.values())}"
            )

        _assert_no_conflicting_financing(self._financing, project_id, code)

        if approved_amount <= 0:
            raise ValidationError("Montante solicitado deve ser positivo")

        direct_decision = (decision or "pending").strip().lower()
        if actor.role == UserRole.FINANCIAL:
            direct_decision = "pending"
        elif actor.role == UserRole.ADMIN and direct_decision == "pending":
            direct_decision = "pending"
        elif actor.role == UserRole.ADMIN and direct_decision not in (
            "approved",
            "conditional",
            "rejected",
            "pending",
        ):
            raise ValidationError("Decisão inválida")

        if direct_decision == "pending":
            workflow_status = "pending_bank"
            final_decision = "pending"
            disbursed = Decimal("0")
            monitoring = "on_track"
        else:
            if direct_decision not in ("approved", "conditional", "rejected"):
                raise ValidationError("Decisão inválida")
            if approved_amount <= 0 and direct_decision != "rejected":
                raise ValidationError("Montante aprovado deve ser positivo")
            workflow_status = "rejected" if direct_decision == "rejected" else "active"
            final_decision = direct_decision
            disbursed = disbursed_amount if disbursed_amount is not None else Decimal("0")
            monitoring = "on_track"

        created = self._financing.create(
            project_id=project_id,
            bank_code=code,
            submission_id=submission_id,
            decision=final_decision,
            workflow_status=workflow_status,
            approved_amount=approved_amount,
            currency=currency,
            interest_rate_pct=interest_rate_pct,
            term_months=term_months,
            disbursed_amount=disbursed,
            notes=notes,
            submitted_by=actor_id,
            decided_by=actor_id,
        )

        if created.is_portfolio_active():
            items = self._cost_items.find_by_project(project_id)
            spent, _, _ = summarize_project_spend(items)
            monitoring = compute_monitoring_status(
                approved_amount=approved_amount,
                spent_total=spent,
                investment_amount=Decimal(str(project.investment_amount or 0)),
            )
            created = self._financing.update_monitoring_status(created.id, monitoring)
        elif created.is_pending_bank():
            created = self._financing.update_monitoring_status(created.id, monitoring)
            self._activity.append(
                bank_code=code,
                action="financing_submitted",
                summary=f"Pedido de financiamento submetido: {approved_amount} {currency}",
                financing_id=created.id,
                project_id=project_id,
                actor_id=actor_id,
                actor_name=actor.full_name,
                metadata={"project_name": project.name},
            )

        return _financing_output(
            created,
            project_name=project.name,
            company_name=project.company_name,
            sector=project.sector.value,
        )


class DecideProjectFinancingUseCase:
    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        financing_repo: IProjectFinancingRepository,
        cost_items: ICostItemRepository,
        policy: FinancierAccessPolicy,
        activity: IFinancingActivityRepository,
    ) -> None:
        self._users = users
        self._projects = projects
        self._financing = financing_repo
        self._cost_items = cost_items
        self._policy = policy
        self._activity = activity

    def execute(
        self,
        *,
        actor_id: UUID,
        financing_id: UUID,
        decision: str,
        approved_amount: Decimal | None = None,
        disbursed_amount: Decimal | None = None,
        interest_rate_pct: Decimal | None = None,
        term_months: int | None = None,
        notes: str | None = None,
    ) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        financing = self._financing.find_by_id(financing_id)
        if financing is None or not financing.is_active:
            raise EntityNotFoundError("Financiamento", str(financing_id))
        if not financing.is_pending_bank():
            raise ValidationError("Este pedido já foi decidido ou não está pendente.")
        if not self._policy.can_decide_financing(actor, financing):
            raise AuthorizationError("Sem permissão para decidir este financiamento")

        project = self._projects.find_by_id(financing.project_id)
        if project is None:
            raise EntityNotFoundError("Projeto", str(financing.project_id))

        code = decision.strip().lower()
        if code not in ("approved", "conditional", "rejected"):
            raise ValidationError("Decisão inválida")

        amount = approved_amount if approved_amount is not None else financing.approved_amount
        if code != "rejected" and amount <= 0:
            raise ValidationError("Montante aprovado deve ser positivo")

        disbursed = disbursed_amount if disbursed_amount is not None else Decimal("0")
        workflow_status = "rejected" if code == "rejected" else "active"
        monitoring = "on_track"
        if workflow_status == "active":
            items = self._cost_items.find_by_project(project.id)
            spent, _, _ = summarize_project_spend(items)
            monitoring = compute_monitoring_status(
                approved_amount=amount,
                spent_total=spent,
                investment_amount=Decimal(str(project.investment_amount or 0)),
            )

        now = datetime.now(timezone.utc)
        updated = self._financing.apply_bank_decision(
            financing_id,
            decision=code,
            workflow_status=workflow_status,
            approved_amount=amount,
            disbursed_amount=disbursed if workflow_status == "active" else Decimal("0"),
            interest_rate_pct=interest_rate_pct if interest_rate_pct is not None else financing.interest_rate_pct,
            term_months=term_months if term_months is not None else financing.term_months,
            notes=notes if notes is not None else financing.notes,
            bank_decided_by=actor_id,
            bank_decided_at=now,
            monitoring_status=monitoring,
        )

        action = "financing_rejected" if code == "rejected" else "financing_approved"
        summary_pt = {
            "approved": f"Financiamento aprovado: {amount} {financing.currency}",
            "conditional": f"Financiamento aprovado com condições: {amount} {financing.currency}",
            "rejected": "Pedido de financiamento recusado",
        }[code]
        self._activity.append(
            bank_code=financing.bank_code,
            action=action,
            summary=summary_pt,
            financing_id=financing_id,
            project_id=project.id,
            actor_id=actor_id,
            actor_name=actor.full_name,
            metadata={"decision": code, "project_name": project.name},
        )

        return _financing_output(
            updated,
            project_name=project.name,
            company_name=project.company_name,
            sector=project.sector.value,
        )


class ListProjectFinancingsUseCase:
    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        financing_repo: IProjectFinancingRepository,
        policy: FinancierAccessPolicy,
    ) -> None:
        self._users = users
        self._projects = projects
        self._financing = financing_repo
        self._policy = policy

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        project = self._projects.find_by_id(project_id)
        if project is None:
            raise EntityNotFoundError("Projeto", str(project_id))

        rows = self._financing.find_by_project(project_id, active_only=True)
        visible = [
            f
            for f in rows
            if self._policy.can_view_financing(actor, f, project=project)
        ]
        return {
            "items": [
                _financing_output(
                    f,
                    project_name=project.name,
                    company_name=project.company_name,
                    sector=project.sector.value,
                )
                for f in visible
            ],
            "total": len(visible),
        }


class ListFinancierPendingApprovalsUseCase:
    def __init__(
        self,
        users: IUserRepository,
        projects: IProjectRepository,
        financing_repo: IProjectFinancingRepository,
        policy: FinancierAccessPolicy,
    ) -> None:
        self._users = users
        self._projects = projects
        self._financing = financing_repo
        self._policy = policy

    def execute(self, *, actor_id: UUID) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))
        if actor.role not in (UserRole.ADMIN, UserRole.BANK):
            raise AuthorizationError("Sem acesso")

        bank_filter = self._policy.portfolio_bank_code(actor)
        if actor.role == UserRole.ADMIN:
            rows = self._financing.list_all_pending()
        elif bank_filter:
            rows = self._financing.list_pending_by_bank(bank_filter)
        else:
            rows = []

        items: list[dict] = []
        for f in rows:
            project = self._projects.find_by_id(f.project_id)
            if project is None:
                continue
            if actor.role != UserRole.ADMIN and not self._policy.can_decide_financing(actor, f):
                continue
            items.append(
                _financing_output(
                    f,
                    project_name=project.name,
                    company_name=project.company_name,
                    sector=project.sector.value,
                )
            )
        return {"items": items, "total": len(items)}


class ListFinancierPortfolioUseCase:
    def __init__(self, loader) -> None:
        from app.application.services.financier_portfolio_loader import FinancierPortfolioLoader

        self._loader: FinancierPortfolioLoader = loader

    def execute(self, *, actor_id: UUID) -> dict:
        actor, visible, bank_filter = self._loader.load_visible_financings(actor_id)
        items = []
        stats = {"on_track": 0, "attention": 0, "critical": 0}
        total_exposure = Decimal("0")

        for f in visible:
            project = self._loader._projects.find_by_id(f.project_id)
            if project is None:
                continue
            row = self._loader.enrich_item(f, project)
            items.append(row)
            stats[row["monitoring_status"]] = stats.get(row["monitoring_status"], 0) + 1
            total_exposure += f.approved_amount

        return {
            "items": items,
            "total": len(items),
            "stats": {
                "on_track": stats["on_track"],
                "attention": stats["attention"],
                "critical": stats["critical"],
                "total_exposure": str(total_exposure),
            },
            "viewer_bank": _bank_meta(bank_filter) if bank_filter else None,
        }


class GetFinancierMonitoringUseCase:
    """Compatível com UI anterior; delega no detalhe completo."""

    def __init__(self, detail_use_case) -> None:
        self._detail = detail_use_case

    def execute(self, *, actor_id: UUID, financing_id: UUID) -> dict:
        full = self._detail.execute(actor_id=actor_id, financing_id=financing_id)
        return {
            "financing": full["financing"],
            "project": full["project"],
            "charts": full["charts"],
            "monitoring_status": full["monitoring_status"],
            "financial": full.get("financial"),
            "physical": full.get("physical"),
            "schedule": full.get("schedule"),
            "alerts": full.get("alerts"),
            "disbursements": full.get("disbursements"),
            "documents": full.get("documents"),
            "activity": full.get("activity"),
            "workflow": full.get("workflow"),
            "terminal": full.get("terminal"),
        }
