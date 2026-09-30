from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

from app.domain.entities.cost_item import CostItem
from app.domain.enums.cost_item_type import CostItemType
from app.domain.enums.currency import Currency
from app.domain.enums.data_source import DataSource


class ICostItemRepository(ABC):
    @abstractmethod
    def find_by_id(self, item_id: UUID) -> CostItem | None:
        ...

    @abstractmethod
    def find_by_project(
        self, project_id: UUID, *, item_type: CostItemType | None = None
    ) -> list[CostItem]:
        ...

    @abstractmethod
    def count_by_project(self, project_id: UUID) -> int:
        ...

    @abstractmethod
    def summarize_spend_by_project(
        self, project_id: UUID
    ) -> tuple[Decimal, Decimal, Decimal]:
        """Total gasto, CAPEX e OPEX (sem carregar linhas completas)."""
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def create_many(self, items: list[dict]) -> list[CostItem]:
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def delete(self, item_id: UUID) -> None:
        ...
