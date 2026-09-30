from decimal import Decimal
from uuid import UUID

from supabase import Client

from app.domain.entities.cost_item import CostItem
from app.domain.enums.cost_item_type import CostItemType
from app.domain.enums.currency import Currency
from app.domain.enums.data_source import DataSource
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from app.domain.repositories.cost_item_repository import ICostItemRepository
from app.infrastructure.supabase.ingestion_mappers import map_cost_item
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


class SupabaseCostItemRepository(ICostItemRepository):
    TABLE = "cost_items"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_by_id(self, item_id: UUID) -> CostItem | None:
        response = (
            self._client.table(self.TABLE).select("*").eq("id", str(item_id)).limit(1).execute()
        )
        row = get_single_row(response)
        return map_cost_item(row) if row else None

    def find_by_project(
        self, project_id: UUID, *, item_type: CostItemType | None = None
    ) -> list[CostItem]:
        query = self._client.table(self.TABLE).select("*").eq("project_id", str(project_id))
        if item_type:
            query = query.eq("item_type", item_type.value)
        response = query.order("created_at", desc=False).execute()
        return [map_cost_item(r) for r in get_rows(response)]

    def count_by_project(self, project_id: UUID) -> int:
        response = (
            self._client.table(self.TABLE)
            .select("id", count="exact")
            .eq("project_id", str(project_id))
            .execute()
        )
        return response.count or 0

    def summarize_spend_by_project(
        self, project_id: UUID
    ) -> tuple[Decimal, Decimal, Decimal]:
        response = (
            self._client.table(self.TABLE)
            .select("item_type,total_amount")
            .eq("project_id", str(project_id))
            .execute()
        )
        spent = Decimal("0")
        capex = Decimal("0")
        opex = Decimal("0")
        for row in get_rows(response):
            total = Decimal(str(row.get("total_amount") or 0))
            spent += total
            if row.get("item_type") == CostItemType.CAPEX.value:
                capex += total
            else:
                opex += total
        return spent, capex, opex

    def create(
        self,
        *,
        project_id: UUID,
        item_type: CostItemType,
        category: str,
        description: str,
        quantity: Decimal,
        unit: str,
        unit_price: Decimal,
        currency: Currency,
        source: DataSource,
        data_hash: str,
        supplier_name: str | None,
        supplier_nif: str | None,
        supplier_url: str | None,
        scraping_result_id: UUID | None,
        metadata: dict,
        created_by: UUID,
    ) -> CostItem:
        total = (quantity * unit_price).quantize(Decimal("0.01"))
        payload = {
            "project_id": str(project_id),
            "item_type": item_type.value,
            "category": category,
            "description": description,
            "quantity": str(quantity),
            "unit": unit,
            "unit_price": str(unit_price),
            "total_amount": str(total),
            "currency": currency.value,
            "source": source.value,
            "data_hash": data_hash,
            "supplier_name": supplier_name,
            "supplier_nif": supplier_nif,
            "supplier_url": supplier_url,
            "scraping_result_id": str(scraping_result_id) if scraping_result_id else None,
            "metadata": metadata,
            "created_by": str(created_by),
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        rows = get_rows(response)
        if not rows:
            raise RuntimeError("Falha ao criar item de custo")
        return map_cost_item(rows[0])

    def create_many(self, items: list[dict]) -> list[CostItem]:
        if not items:
            return []
        response = self._client.table(self.TABLE).insert(items).execute()
        return [map_cost_item(r) for r in get_rows(response)]

    def update(
        self,
        item_id: UUID,
        *,
        category: str | None = None,
        description: str | None = None,
        quantity: Decimal | None = None,
        unit: str | None = None,
        unit_price: Decimal | None = None,
        data_hash: str | None = None,
        supplier_name: str | None = None,
        supplier_nif: str | None = None,
        supplier_url: str | None = None,
        metadata: dict | None = None,
    ) -> CostItem:
        existing = self.find_by_id(item_id)
        if existing is None:
            raise EntityNotFoundError("Item de custo", str(item_id))

        qty = quantity if quantity is not None else existing.quantity
        price = unit_price if unit_price is not None else existing.unit_price
        total = (qty * price).quantize(Decimal("0.01"))

        payload: dict = {"total_amount": str(total)}
        if category is not None:
            payload["category"] = category
        if description is not None:
            payload["description"] = description
        if quantity is not None:
            payload["quantity"] = str(quantity)
        if unit is not None:
            payload["unit"] = unit
        if unit_price is not None:
            payload["unit_price"] = str(unit_price)
        if data_hash is not None:
            payload["data_hash"] = data_hash
        if supplier_name is not None:
            payload["supplier_name"] = supplier_name
        if supplier_nif is not None:
            payload["supplier_nif"] = supplier_nif
        if supplier_url is not None:
            payload["supplier_url"] = supplier_url
        if metadata is not None:
            payload["metadata"] = metadata

        response = (
            self._client.table(self.TABLE).update(payload).eq("id", str(item_id)).execute()
        )
        rows = get_rows(response)
        if not rows:
            raise EntityNotFoundError("Item de custo", str(item_id))
        return map_cost_item(rows[0])

    def delete(self, item_id: UUID) -> None:
        self._client.table(self.TABLE).delete().eq("id", str(item_id)).execute()
