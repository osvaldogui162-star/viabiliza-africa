from dataclasses import asdict
from uuid import UUID

from app.application.interfaces.hash_service import IHashService
from app.application.interfaces.qr_code_service import IQRCodeService
from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.use_cases.ingestion.mappers import to_budget_output, to_proforma_output
from app.config import Config
from app.domain.enums.audit_action import AuditAction
from app.domain.enums.audit_entity_type import AuditEntityType
from app.domain.enums.budget_status import BudgetStatus
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, ValidationError
from app.domain.repositories.audit_trail_repository import IAuditTrailRepository
from app.domain.repositories.budget_repository import IBudgetRepository
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.domain.repositories.admin_config_repository import IBudgetTemplateRepository
from app.domain.repositories.project_repository import IProjectRepository
from app.application.use_cases.admin.mappers import to_template_output


class GenerateBudgetUseCase:
    """UC16 — Gerar orçamento rastreável com QR Code."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        cost_item_repository: ICostItemRepository,
        budget_repository: IBudgetRepository,
        audit_trail_repository: IAuditTrailRepository,
        hash_service: IHashService,
        qr_service: IQRCodeService,
        config: Config,
        template_repository: IBudgetTemplateRepository | None = None,
    ) -> None:
        self._ctx = context_resolver
        self._items = cost_item_repository
        self._budgets = budget_repository
        self._audit = audit_trail_repository
        self._hash = hash_service
        self._qr = qr_service
        self._config = config
        self._templates = template_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        title: str,
        ip_address: str | None = None,
    ):
        ctx = self._ctx.resolve(actor_id, project_id)
        self._ctx.require_ingest(ctx)

        items = self._items.find_by_project(project_id)
        if not items:
            raise ValidationError("Projeto não tem itens de custo para gerar orçamento")

        item_hashes = [item.data_hash for item in items]
        verification_hash = self._hash.hash_chain(*item_hashes)
        budget_number = self._budgets.next_budget_number()
        total = sum(item.total_amount for item in items)

        verify_url = f"{self._config.FRONTEND_BASE_URL}/verify/budget/{verification_hash}"

        qr = self._qr.generate(verify_url)

        budget_items_payload = []
        for index, item in enumerate(items):
            budget_items_payload.append(
                {
                    "cost_item_id": str(item.id),
                    "item_type": item.item_type.value,
                    "category": item.category,
                    "description": item.description,
                    "quantity": str(item.quantity),
                    "unit": item.unit,
                    "unit_price": str(item.unit_price),
                    "total_amount": str(item.total_amount),
                    "item_hash": item.data_hash,
                    "supplier_name": item.supplier_name,
                    "line_order": index,
                }
            )

        budget = self._budgets.create_budget(
            project_id=project_id,
            budget_number=budget_number,
            title=title.strip() or f"Orçamento {budget_number}",
            total_amount=total,
            currency=ctx.project.currency.value,
            verification_hash=verification_hash,
            qr_code_data=qr.data,
            qr_code_image=qr.image_base64,
            created_by=actor_id,
            items=budget_items_payload,
        )

        self._audit.create(
            project_id=project_id,
            entity_type=AuditEntityType.BUDGET,
            entity_id=budget.id,
            action=AuditAction.BUDGET_GENERATED,
            actor_id=actor_id,
            data_hash=verification_hash,
            ip_address=ip_address,
            metadata={"budget_number": budget_number, "items": len(items)},
        )

        output = to_budget_output(budget, items_count=len(items))
        if self._templates:
            template = self._templates.find_default()
            if template:
                data = asdict(output)
                data["template"] = to_template_output(template)
                return data
        return output


class ApproveBudgetUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        budget_repository: IBudgetRepository,
        project_repository: IProjectRepository,
        audit_trail_repository: IAuditTrailRepository,
    ) -> None:
        self._ctx = context_resolver
        self._budgets = budget_repository
        self._projects = project_repository
        self._audit = audit_trail_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        budget_id: UUID,
        ip_address: str | None = None,
    ):
        ctx = self._ctx.resolve(actor_id, project_id)
        self._ctx.require_ingest(ctx)

        budget = self._budgets.find_by_id(budget_id)
        if budget is None or budget.project_id != project_id:
            raise EntityNotFoundError("Orçamento", str(budget_id))
        if budget.status == BudgetStatus.APPROVED:
            raise ValidationError("Orçamento já aprovado")

        approved = self._budgets.approve_budget(budget_id, actor_id)
        self._projects.set_has_approved_budget(project_id, True)

        self._audit.create(
            project_id=project_id,
            entity_type=AuditEntityType.BUDGET,
            entity_id=budget_id,
            action=AuditAction.BUDGET_APPROVED,
            actor_id=actor_id,
            data_hash=approved.verification_hash,
            ip_address=ip_address,
        )
        return to_budget_output(approved, items_count=len(self._budgets.get_budget_items(budget_id)))


class GenerateProformaUseCase:
    """UC17 — Gerar fatura proforma (orçamento aprovado + QR Code)."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        budget_repository: IBudgetRepository,
        audit_trail_repository: IAuditTrailRepository,
        hash_service: IHashService,
        qr_service: IQRCodeService,
        config: Config,
    ) -> None:
        self._ctx = context_resolver
        self._budgets = budget_repository
        self._audit = audit_trail_repository
        self._hash = hash_service
        self._qr = qr_service
        self._config = config

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        budget_id: UUID,
        client_name: str | None = None,
        client_tax_id: str | None = None,
        notes: str | None = None,
        ip_address: str | None = None,
    ):
        ctx = self._ctx.resolve(actor_id, project_id)
        self._ctx.require_ingest(ctx)

        budget = self._budgets.find_by_id(budget_id)
        if budget is None or budget.project_id != project_id:
            raise EntityNotFoundError("Orçamento", str(budget_id))

        if budget.status != BudgetStatus.APPROVED:
            raise ValidationError(
                "O orçamento deve estar aprovado antes de gerar a fatura proforma"
            )

        resolved_client = (client_name or ctx.project.company_name or "").strip()
        if not resolved_client:
            raise ValidationError("Indique o nome do cliente")

        invoice_number = self._budgets.next_invoice_number()
        verification_hash = self._hash.hash_dict(
            {
                "budget_hash": budget.verification_hash,
                "client": resolved_client,
                "invoice": invoice_number,
            }
        )
        verify_url = (
            f"{self._config.FRONTEND_BASE_URL}/verify/budget/{budget.verification_hash}"
        )
        qr = self._qr.generate(verify_url)

        invoice = self._budgets.create_proforma(
            budget_id=budget_id,
            project_id=project_id,
            invoice_number=invoice_number,
            client_name=resolved_client,
            client_tax_id=client_tax_id or ctx.project.company_tax_id,
            total_amount=budget.total_amount,
            currency=budget.currency,
            verification_hash=verification_hash,
            notes=notes,
            created_by=actor_id,
            qr_code_data=qr.data,
            qr_code_image=qr.image_base64,
        )

        self._audit.create(
            project_id=project_id,
            entity_type=AuditEntityType.PROFORMA,
            entity_id=invoice.id,
            action=AuditAction.PROFORMA_GENERATED,
            actor_id=actor_id,
            data_hash=verification_hash,
            ip_address=ip_address,
            metadata={
                "budget_id": str(budget_id),
                "invoice_number": invoice.invoice_number,
                "verify_url": verify_url,
            },
        )
        output = to_proforma_output(invoice)
        result = asdict(output)
        result["verify_url"] = verify_url
        return result


class ListProformasUseCase:
    """Listar faturas proforma do projecto."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        budget_repository: IBudgetRepository,
    ) -> None:
        self._ctx = context_resolver
        self._budgets = budget_repository

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        self._ctx.resolve(actor_id, project_id)
        items = self._budgets.find_proformas_by_project(project_id)
        return {
            "items": [to_proforma_output(i) for i in items],
            "total": len(items),
        }


class ListBudgetsUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        budget_repository: IBudgetRepository,
    ) -> None:
        self._ctx = context_resolver
        self._budgets = budget_repository

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        self._ctx.resolve(actor_id, project_id)
        budgets = self._budgets.find_by_project(project_id)
        return {
            "items": [
                to_budget_output(b, items_count=len(self._budgets.get_budget_items(b.id)))
                for b in budgets
            ],
            "total": len(budgets),
        }


class GetBudgetUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        budget_repository: IBudgetRepository,
    ) -> None:
        self._ctx = context_resolver
        self._budgets = budget_repository

    def execute(self, *, actor_id: UUID, project_id: UUID, budget_id: UUID) -> dict:
        self._ctx.resolve(actor_id, project_id)
        budget = self._budgets.find_by_id(budget_id)
        if budget is None or budget.project_id != project_id:
            raise EntityNotFoundError("Orçamento", str(budget_id))
        items = self._budgets.get_budget_items(budget_id)
        from app.application.use_cases.ingestion.mappers import to_cost_item_output

        return {
            "budget": to_budget_output(budget, items_count=len(items)),
            "items": [
                {
                    "cost_item_id": str(i.cost_item_id),
                    "item_type": i.item_type.value,
                    "category": i.category,
                    "description": i.description,
                    "quantity": format(i.quantity, "f"),
                    "unit": i.unit,
                    "unit_price": format(i.unit_price, "f"),
                    "total_amount": format(i.total_amount, "f"),
                    "item_hash": i.item_hash,
                    "supplier_name": i.supplier_name,
                }
                for i in items
            ],
        }


class VerifyBudgetUseCase:
    """UC36 — Verificação pública de orçamento via hash (QR Code)."""

    def __init__(
        self,
        budget_repository: IBudgetRepository,
        project_repository: IProjectRepository,
        cost_item_repository: ICostItemRepository,
    ) -> None:
        self._budgets = budget_repository
        self._projects = project_repository
        self._items = cost_item_repository

    def execute(self, verification_hash: str) -> dict:
        budget = self._budgets.find_by_verification_hash(verification_hash)
        if budget is None:
            raise ValidationError("Orçamento não encontrado ou foi alterado")

        project = self._projects.find_by_id(budget.project_id)
        budget_items = self._budgets.get_budget_items(budget.id)
        cost_items = {str(i.id): i for i in self._items.find_by_project(budget.project_id)}

        items_output = []
        for bi in budget_items:
            cost = cost_items.get(str(bi.cost_item_id))
            source = cost.source.value if cost else "unknown"
            source_label = None
            if cost and cost.metadata:
                source_label = cost.metadata.get("source_display") or cost.metadata.get(
                    "price_source"
                )
            items_output.append(
                {
                    "item_type": bi.item_type.value,
                    "category": bi.category,
                    "description": bi.description,
                    "quantity": format(bi.quantity, "f"),
                    "unit": bi.unit,
                    "unit_price": format(bi.unit_price, "f"),
                    "total_amount": format(bi.total_amount, "f"),
                    "item_hash": bi.item_hash,
                    "supplier_name": bi.supplier_name,
                    "source": source,
                    "source_label": source_label,
                }
            )

        return {
            "valid": True,
            "project_id": str(budget.project_id),
            "project_name": project.name if project else None,
            "company_name": project.company_name if project else None,
            "budget_number": budget.budget_number,
            "title": budget.title,
            "status": budget.status.value,
            "total_amount": format(budget.total_amount, "f"),
            "currency": budget.currency,
            "verification_hash": budget.verification_hash,
            "items_count": len(items_output),
            "approved_at": budget.approved_at.isoformat() if budget.approved_at else None,
            "created_at": budget.created_at.isoformat(),
            "generated_at": budget.created_at.isoformat(),
            "items": items_output,
        }
