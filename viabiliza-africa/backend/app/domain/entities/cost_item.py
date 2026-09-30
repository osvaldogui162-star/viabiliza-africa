from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.enums.cost_item_type import CostItemType
from app.domain.enums.currency import Currency
from app.domain.enums.data_source import DataSource


@dataclass
class CostItem:
    id: UUID
    project_id: UUID
    item_type: CostItemType
    category: str
    description: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    total_amount: Decimal
    currency: Currency
    source: DataSource
    data_hash: str
    supplier_name: str | None
    supplier_nif: str | None
    supplier_url: str | None
    scraping_result_id: UUID | None
    metadata: dict
    created_by: UUID
    created_at: datetime
    updated_at: datetime
