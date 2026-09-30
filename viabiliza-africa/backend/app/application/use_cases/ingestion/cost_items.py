from decimal import Decimal
from uuid import UUID

from app.application.interfaces.excel_parser import IExcelParser
from app.application.interfaces.hash_service import IHashService
from app.application.services.cost_item_hash_builder import CostItemHashBuilder
from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.use_cases.ingestion.mappers import to_cost_item_output
from app.domain.enums.audit_action import AuditAction
from app.domain.enums.audit_entity_type import AuditEntityType
from app.domain.enums.cost_item_type import CostItemType
from app.domain.enums.data_source import DataSource
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, ValidationError
from app.domain.repositories.audit_trail_repository import IAuditTrailRepository
from app.domain.repositories.budget_repository import IBudgetRepository
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.infrastructure.scraping.agt_nif_lookup import AgtNifLookupService


class CreateCostItemUseCase:
    """UC12 — Importar dados manualmente (fornecedor via NIF/AGT)."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        cost_item_repository: ICostItemRepository,
        audit_trail_repository: IAuditTrailRepository,
        hash_builder: CostItemHashBuilder,
        nif_lookup: AgtNifLookupService,
    ) -> None:
        self._ctx = context_resolver
        self._items = cost_item_repository
        self._audit = audit_trail_repository
        self._hash_builder = hash_builder
        self._nif = nif_lookup

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        item_type: str,
        category: str,
        description: str,
        quantity: Decimal,
        unit: str,
        unit_price: Decimal,
        supplier_nif: str | None = None,
        supplier_name: str | None = None,
        ip_address: str | None = None,
    ):
        ctx = self._ctx.resolve(actor_id, project_id)
        self._ctx.require_ingest(ctx)
        self._validate(item_type, category, description, quantity, unit_price)

        cleaned_nif = (supplier_nif or "").strip().upper().replace(" ", "")
        resolved_name = (supplier_name or "").strip() or None
        metadata: dict = {
            "source_display": "Manual",
            "price_source": "manual",
        }

        if cleaned_nif:
            try:
                company = self._nif.lookup(cleaned_nif)
            except ValueError as exc:
                raise ValidationError(str(exc)) from exc
            except LookupError as exc:
                raise ValidationError(str(exc)) from exc
            except Exception as exc:
                raise ValidationError(
                    f"Falha ao consultar NIF do fornecedor na AGT: {exc}"
                ) from exc

            resolved_name = company.company_name
            metadata = {
                "supplier": {
                    "nif": company.nif,
                    "name": company.company_name,
                    "address": company.address,
                    "activity": company.activity,
                    "status": company.status,
                    "source_url": company.source_url,
                    "fields": company.raw_fields,
                }
            }

        item_type_enum = CostItemType(item_type)
        data_hash = self._hash_builder.build_hash(
            project_id=project_id,
            item_type=item_type_enum,
            category=category,
            description=description,
            quantity=quantity,
            unit=unit,
            unit_price=unit_price,
            source=DataSource.MANUAL,
            supplier_name=resolved_name,
        )

        item = self._items.create(
            project_id=project_id,
            item_type=item_type_enum,
            category=category.strip(),
            description=description.strip(),
            quantity=quantity,
            unit=unit.strip(),
            unit_price=unit_price,
            currency=ctx.project.currency,
            source=DataSource.MANUAL,
            data_hash=data_hash,
            supplier_name=resolved_name,
            supplier_nif=cleaned_nif or None,
            supplier_url=None,
            scraping_result_id=None,
            metadata=metadata,
            created_by=actor_id,
        )

        self._audit.create(
            project_id=project_id,
            entity_type=AuditEntityType.COST_ITEM,
            entity_id=item.id,
            action=AuditAction.CREATED,
            actor_id=actor_id,
            data_hash=data_hash,
            ip_address=ip_address,
            metadata={
                "source": "manual",
                "supplier_nif": cleaned_nif or None,
            },
        )
        return to_cost_item_output(item)

    @staticmethod
    def _validate(item_type, category, description, quantity, unit_price) -> None:
        if not CostItemType.is_valid(item_type):
            raise ValidationError("Tipo deve ser 'opex' ou 'capex'")
        if not category.strip() or not description.strip():
            raise ValidationError("Categoria e descrição são obrigatórias")
        if quantity <= 0 or unit_price < 0:
            raise ValidationError("Quantidade e preço inválidos")


class ImportCostItemsExcelUseCase:
    """UC13 — Importar dados via Excel (máx. 1000 linhas)."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        cost_item_repository: ICostItemRepository,
        audit_trail_repository: IAuditTrailRepository,
        hash_builder: CostItemHashBuilder,
        hash_service: IHashService,
        excel_parser: IExcelParser,
    ) -> None:
        self._ctx = context_resolver
        self._items = cost_item_repository
        self._audit = audit_trail_repository
        self._hash_builder = hash_builder
        self._hash = hash_service
        self._excel = excel_parser

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        file_bytes: bytes,
        ip_address: str | None = None,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        self._ctx.require_ingest(ctx)

        rows = self._excel.parse_cost_items(file_bytes)
        payloads = []

        for row in rows:
            item_type = CostItemType(row.item_type)
            supplier_nif = getattr(row, "supplier_nif", None)
            data_hash = self._hash_builder.build_hash(
                project_id=project_id,
                item_type=item_type,
                category=row.category,
                description=row.description,
                quantity=row.quantity,
                unit=row.unit,
                unit_price=row.unit_price,
                source=DataSource.EXCEL,
                supplier_name=row.supplier_name,
            )
            total = (row.quantity * row.unit_price).quantize(Decimal("0.01"))
            payloads.append(
                {
                    "project_id": str(project_id),
                    "item_type": item_type.value,
                    "category": row.category,
                    "description": row.description,
                    "quantity": str(row.quantity),
                    "unit": row.unit,
                    "unit_price": str(row.unit_price),
                    "total_amount": str(total),
                    "currency": ctx.project.currency.value,
                    "source": DataSource.EXCEL.value,
                    "data_hash": data_hash,
                    "supplier_name": row.supplier_name,
                    "supplier_nif": supplier_nif,
                    "metadata": {
                        "import_row": True,
                        "source_display": "Excel",
                        "price_source": "excel",
                    },
                    "created_by": str(actor_id),
                }
            )

        created_items = self._items.create_many(payloads)

        chain_hash = self._hash.hash_chain(*[item.data_hash for item in created_items])
        self._audit.create(
            project_id=project_id,
            entity_type=AuditEntityType.COST_ITEM,
            entity_id=project_id,
            action=AuditAction.IMPORTED,
            actor_id=actor_id,
            data_hash=chain_hash,
            ip_address=ip_address,
            metadata={"count": len(created_items), "source": "excel"},
        )

        return {
            "imported": len(created_items),
            "items": [to_cost_item_output(i) for i in created_items],
        }


class ListCostItemsUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        cost_item_repository: ICostItemRepository,
    ) -> None:
        self._ctx = context_resolver
        self._items = cost_item_repository

    def execute(
        self, *, actor_id: UUID, project_id: UUID, item_type: str | None = None
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        parsed_type = CostItemType(item_type) if item_type else None
        items = self._items.find_by_project(project_id, item_type=parsed_type)
        return {
            "items": [to_cost_item_output(i) for i in items],
            "total": len(items),
        }


class DeleteCostItemUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        cost_item_repository: ICostItemRepository,
        audit_trail_repository: IAuditTrailRepository,
        budget_repository: IBudgetRepository | None = None,
    ) -> None:
        self._ctx = context_resolver
        self._items = cost_item_repository
        self._audit = audit_trail_repository
        self._budgets = budget_repository

    def execute(
        self, *, actor_id: UUID, project_id: UUID, item_id: UUID, ip_address: str | None = None
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        self._ctx.require_ingest(ctx)
        item = self._items.find_by_id(item_id)
        if item is None or item.project_id != project_id:
            raise EntityNotFoundError("Item de custo", str(item_id))

        previous = self._audit.get_last_hash_for_entity(
            AuditEntityType.COST_ITEM, item_id
        )
        # budget_items.cost_item_id → ON DELETE RESTRICT
        if self._budgets is not None:
            self._budgets.delete_budget_items_by_cost_item(item_id)
        self._items.delete(item_id)
        self._audit.create(
            project_id=project_id,
            entity_type=AuditEntityType.COST_ITEM,
            entity_id=item_id,
            action=AuditAction.DELETED,
            actor_id=actor_id,
            data_hash=item.data_hash,
            previous_hash=previous,
            ip_address=ip_address,
        )
        return {"message": "Item removido com sucesso"}


class UpdateCostItemUseCase:
    """Actualizar item de custo manualmente (re-hash SHA-256)."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        cost_item_repository: ICostItemRepository,
        audit_trail_repository: IAuditTrailRepository,
        hash_builder: CostItemHashBuilder,
    ) -> None:
        self._ctx = context_resolver
        self._items = cost_item_repository
        self._audit = audit_trail_repository
        self._hash_builder = hash_builder

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        item_id: UUID,
        category: str | None = None,
        description: str | None = None,
        quantity: Decimal | None = None,
        unit: str | None = None,
        unit_price: Decimal | None = None,
        ip_address: str | None = None,
    ):
        ctx = self._ctx.resolve(actor_id, project_id)
        self._ctx.require_ingest(ctx)

        item = self._items.find_by_id(item_id)
        if item is None or item.project_id != project_id:
            raise EntityNotFoundError("Item de custo", str(item_id))

        new_category = category.strip() if category else item.category
        new_description = description.strip() if description else item.description
        new_quantity = quantity if quantity is not None else item.quantity
        new_unit = unit.strip() if unit else item.unit
        new_unit_price = unit_price if unit_price is not None else item.unit_price

        if not new_category or not new_description:
            raise ValidationError("Categoria e descrição são obrigatórias")
        if new_quantity <= 0 or new_unit_price < 0:
            raise ValidationError("Quantidade e preço inválidos")

        data_hash = self._hash_builder.build_hash(
            project_id=project_id,
            item_type=item.item_type,
            category=new_category,
            description=new_description,
            quantity=new_quantity,
            unit=new_unit,
            unit_price=new_unit_price,
            source=item.source,
            supplier_name=item.supplier_name,
        )

        metadata = dict(item.metadata or {})
        metadata["last_manual_edit"] = True

        updated = self._items.update(
            item_id,
            category=new_category,
            description=new_description,
            quantity=new_quantity,
            unit=new_unit,
            unit_price=new_unit_price,
            data_hash=data_hash,
            metadata=metadata,
        )

        previous = self._audit.get_last_hash_for_entity(
            AuditEntityType.COST_ITEM, item_id
        )
        self._audit.create(
            project_id=project_id,
            entity_type=AuditEntityType.COST_ITEM,
            entity_id=item_id,
            action=AuditAction.UPDATED,
            actor_id=actor_id,
            data_hash=data_hash,
            previous_hash=previous,
            ip_address=ip_address,
            metadata={"source": item.source.value},
        )
        return to_cost_item_output(updated)
