from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.enums.budget_status import BudgetStatus
from app.domain.enums.cost_item_type import CostItemType


@dataclass
class Budget:
    id: UUID
    project_id: UUID
    budget_number: str
    title: str
    total_amount: Decimal
    currency: str
    status: BudgetStatus
    verification_hash: str
    qr_code_data: str
    qr_code_image: str
    created_by: UUID
    approved_by: UUID | None
    approved_at: datetime | None
    created_at: datetime
    updated_at: datetime


@dataclass
class BudgetItem:
    id: UUID
    budget_id: UUID
    cost_item_id: UUID
    item_type: CostItemType
    category: str
    description: str
    quantity: Decimal
    unit: str
    unit_price: Decimal
    total_amount: Decimal
    item_hash: str
    supplier_name: str | None
    line_order: int


@dataclass
class ProformaInvoice:
    id: UUID
    budget_id: UUID
    project_id: UUID
    invoice_number: str
    client_name: str
    client_tax_id: str | None
    total_amount: Decimal
    currency: str
    verification_hash: str
    notes: str | None
    created_by: UUID
    issued_at: datetime
    qr_code_data: str | None = None
    qr_code_image: str | None = None
