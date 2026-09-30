from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class FinancingDisbursement:
    id: UUID
    financing_id: UUID
    requested_amount: Decimal
    approved_amount: Decimal | None
    paid_amount: Decimal
    currency: str
    status: str
    purpose: str | None
    requested_by: UUID
    reviewed_by: UUID | None
    requested_at: datetime
    decided_at: datetime | None
    paid_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


@dataclass
class FinancingDocument:
    id: UUID
    financing_id: UUID
    doc_type: str
    title: str
    file_ref: str | None
    validation_status: str
    uploaded_by: UUID
    validated_by: UUID | None
    validated_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


@dataclass
class FinancingPortalActivity:
    id: UUID
    bank_code: str
    financing_id: UUID | None
    project_id: UUID | None
    actor_id: UUID | None
    actor_name: str | None
    action: str
    summary: str
    metadata: dict
    created_at: datetime
