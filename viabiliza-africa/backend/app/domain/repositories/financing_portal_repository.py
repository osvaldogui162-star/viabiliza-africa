from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

from app.domain.entities.financing_portal_ops import (
    FinancingDisbursement,
    FinancingDocument,
    FinancingPortalActivity,
)


class IFinancingDisbursementRepository(ABC):
    @abstractmethod
    def create(
        self,
        *,
        financing_id: UUID,
        requested_amount: Decimal,
        currency: str,
        purpose: str | None,
        requested_by: UUID,
    ) -> FinancingDisbursement:
        ...

    @abstractmethod
    def find_by_id(self, disbursement_id: UUID) -> FinancingDisbursement | None:
        ...

    @abstractmethod
    def list_by_financing(self, financing_id: UUID) -> list[FinancingDisbursement]:
        ...

    @abstractmethod
    def list_by_financing_ids(self, financing_ids: list[UUID]) -> list[FinancingDisbursement]:
        ...

    @abstractmethod
    def list_by_bank_financing_ids(
        self, financing_ids: list[UUID], *, status: str | None = None
    ) -> list[FinancingDisbursement]:
        ...

    @abstractmethod
    def update_status(
        self,
        disbursement_id: UUID,
        *,
        status: str,
        reviewed_by: UUID | None = None,
        approved_amount: Decimal | None = None,
        paid_amount: Decimal | None = None,
        notes: str | None = None,
    ) -> FinancingDisbursement:
        ...

    @abstractmethod
    def count_pending_by_financing(self, financing_id: UUID) -> int:
        ...


class IFinancingDocumentRepository(ABC):
    @abstractmethod
    def create(
        self,
        *,
        financing_id: UUID,
        doc_type: str,
        title: str,
        file_ref: str | None,
        uploaded_by: UUID,
    ) -> FinancingDocument:
        ...

    @abstractmethod
    def find_by_id(self, document_id: UUID) -> FinancingDocument | None:
        ...

    @abstractmethod
    def list_by_financing(self, financing_id: UUID) -> list[FinancingDocument]:
        ...

    @abstractmethod
    def list_by_financing_ids(self, financing_ids: list[UUID]) -> list[FinancingDocument]:
        ...

    @abstractmethod
    def update_validation(
        self,
        document_id: UUID,
        *,
        validation_status: str,
        validated_by: UUID,
        notes: str | None = None,
    ) -> FinancingDocument:
        ...

    @abstractmethod
    def count_pending_by_financing(self, financing_id: UUID) -> int:
        ...


class IFinancingActivityRepository(ABC):
    @abstractmethod
    def append(
        self,
        *,
        bank_code: str,
        action: str,
        summary: str,
        financing_id: UUID | None = None,
        project_id: UUID | None = None,
        actor_id: UUID | None = None,
        actor_name: str | None = None,
        metadata: dict | None = None,
    ) -> FinancingPortalActivity:
        ...

    @abstractmethod
    def list_by_bank(self, bank_code: str, *, limit: int = 50) -> list[FinancingPortalActivity]:
        ...

    @abstractmethod
    def list_by_financing(self, financing_id: UUID, *, limit: int = 50) -> list[FinancingPortalActivity]:
        ...
