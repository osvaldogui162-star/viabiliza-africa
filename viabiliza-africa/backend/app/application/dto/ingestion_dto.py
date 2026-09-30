from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class CostItemOutput:
    id: UUID
    project_id: UUID
    item_type: str
    category: str
    description: str
    quantity: str
    unit: str
    unit_price: str
    total_amount: str
    currency: str
    source: str
    source_label: str
    data_hash: str
    supplier_name: str | None
    supplier_nif: str | None
    supplier_url: str | None
    contacts: list[dict]
    metadata: dict
    created_at: datetime


@dataclass(frozen=True)
class ScrapingJobOutput:
    id: UUID
    project_id: UUID
    search_query: str
    sources: list[str]
    status: str
    results_count: int
    created_at: datetime
    completed_at: datetime | None


@dataclass(frozen=True)
class ScrapingResultOutput:
    id: UUID
    job_id: UUID
    source: str
    supplier_name: str
    product_name: str
    price: str
    currency: str
    product_url: str | None
    is_selected: bool
    data_hash: str


@dataclass(frozen=True)
class BudgetOutput:
    id: UUID
    project_id: UUID
    budget_number: str
    title: str
    total_amount: str
    currency: str
    status: str
    verification_hash: str
    qr_code_data: str
    qr_code_image: str
    items_count: int
    approved_at: datetime | None
    created_at: datetime


@dataclass(frozen=True)
class ProformaOutput:
    id: UUID
    budget_id: UUID
    project_id: UUID
    invoice_number: str
    client_name: str
    client_tax_id: str | None
    total_amount: str
    currency: str
    verification_hash: str
    issued_at: datetime
    qr_code_data: str | None = None
    qr_code_image: str | None = None


@dataclass(frozen=True)
class AuditTrailOutput:
    id: UUID
    project_id: UUID
    entity_type: str
    entity_id: UUID
    action: str
    actor_id: UUID | None
    data_hash: str
    previous_hash: str | None
    metadata: dict
    created_at: datetime
