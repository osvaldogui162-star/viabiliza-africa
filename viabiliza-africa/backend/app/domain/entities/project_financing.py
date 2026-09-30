from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class ProjectFinancing:
    id: UUID
    project_id: UUID
    bank_code: str
    submission_id: UUID | None
    decision: str
    workflow_status: str
    approved_amount: Decimal
    currency: str
    interest_rate_pct: Decimal | None
    term_months: int | None
    disbursed_amount: Decimal
    monitoring_status: str
    notes: str | None
    submitted_by: UUID | None
    decided_by: UUID
    decision_at: datetime
    bank_decided_by: UUID | None
    bank_decided_at: datetime | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    def is_portfolio_active(self) -> bool:
        return (
            self.is_active
            and self.workflow_status == "active"
            and self.decision in ("approved", "conditional")
        )

    def is_pending_bank(self) -> bool:
        return self.is_active and self.workflow_status == "pending_bank" and self.decision == "pending"
