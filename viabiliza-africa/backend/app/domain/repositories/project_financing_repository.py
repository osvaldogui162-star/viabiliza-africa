from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.entities.project_financing import ProjectFinancing


class IProjectFinancingRepository(ABC):
    @abstractmethod
    def create(
        self,
        *,
        project_id: UUID,
        bank_code: str,
        submission_id: UUID | None,
        decision: str,
        workflow_status: str,
        approved_amount: Decimal,
        currency: str,
        interest_rate_pct: Decimal | None,
        term_months: int | None,
        disbursed_amount: Decimal,
        notes: str | None,
        submitted_by: UUID | None,
        decided_by: UUID,
    ) -> ProjectFinancing:
        ...

    @abstractmethod
    def find_by_id(self, financing_id: UUID) -> ProjectFinancing | None:
        ...

    @abstractmethod
    def find_by_project(self, project_id: UUID, *, active_only: bool = True) -> list[ProjectFinancing]:
        ...

    @abstractmethod
    def list_by_bank(
        self,
        bank_code: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ProjectFinancing]:
        ...

    @abstractmethod
    def list_pending_by_bank(
        self,
        bank_code: str,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProjectFinancing]:
        ...

    @abstractmethod
    def list_all_pending(self, *, limit: int = 100, offset: int = 0) -> list[ProjectFinancing]:
        ...

    @abstractmethod
    def list_all_active(self, *, limit: int = 200, offset: int = 0) -> list[ProjectFinancing]:
        ...

    @abstractmethod
    def apply_bank_decision(
        self,
        financing_id: UUID,
        *,
        decision: str,
        workflow_status: str,
        approved_amount: Decimal,
        disbursed_amount: Decimal,
        interest_rate_pct: Decimal | None,
        term_months: int | None,
        notes: str | None,
        bank_decided_by: UUID,
        bank_decided_at: datetime,
        monitoring_status: str,
    ) -> ProjectFinancing:
        ...

    @abstractmethod
    def update_monitoring_status(self, financing_id: UUID, status: str) -> ProjectFinancing:
        ...

    @abstractmethod
    def update_disbursed_amount(self, financing_id: UUID, amount: Decimal) -> ProjectFinancing:
        ...
