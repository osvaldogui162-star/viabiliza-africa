from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

from app.domain.entities.budget import Budget, BudgetItem, ProformaInvoice
from app.domain.enums.budget_status import BudgetStatus


class IBudgetRepository(ABC):
    @abstractmethod
    def find_by_id(self, budget_id: UUID) -> Budget | None:
        ...

    @abstractmethod
    def find_by_project(self, project_id: UUID) -> list[Budget]:
        ...

    @abstractmethod
    def find_by_verification_hash(self, verification_hash: str) -> Budget | None:
        ...

    @abstractmethod
    def has_approved_budget(self, project_id: UUID) -> bool:
        ...

    @abstractmethod
    def create_budget(
        self,
        *,
        project_id: UUID,
        budget_number: str,
        title: str,
        total_amount: Decimal,
        currency: str,
        verification_hash: str,
        qr_code_data: str,
        qr_code_image: str,
        created_by: UUID,
        items: list[dict],
    ) -> Budget:
        ...

    @abstractmethod
    def get_budget_items(self, budget_id: UUID) -> list[BudgetItem]:
        ...

    @abstractmethod
    def approve_budget(self, budget_id: UUID, approved_by: UUID) -> Budget:
        ...

    @abstractmethod
    def create_proforma(
        self,
        *,
        budget_id: UUID,
        project_id: UUID,
        invoice_number: str,
        client_name: str,
        client_tax_id: str | None,
        total_amount: Decimal,
        currency: str,
        verification_hash: str,
        notes: str | None,
        created_by: UUID,
        qr_code_data: str | None = None,
        qr_code_image: str | None = None,
    ) -> ProformaInvoice:
        ...

    @abstractmethod
    def find_proforma_by_id(self, invoice_id: UUID) -> ProformaInvoice | None:
        ...

    @abstractmethod
    def find_proformas_by_project(self, project_id: UUID) -> list[ProformaInvoice]:
        ...

    @abstractmethod
    def next_budget_number(self) -> str:
        ...

    @abstractmethod
    def next_invoice_number(self) -> str:
        ...

    @abstractmethod
    def delete_by_project(self, project_id: UUID) -> int:
        """Remove proformas e orçamentos do projecto (e budget_items em cascata)."""
        ...

    @abstractmethod
    def delete_budget_items_by_cost_item(self, cost_item_id: UUID) -> None:
        """Remove linhas de orçamento que referenciam um cost item."""
        ...
