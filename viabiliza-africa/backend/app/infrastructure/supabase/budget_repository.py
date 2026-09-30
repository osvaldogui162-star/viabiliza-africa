from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from supabase import Client

from app.domain.entities.budget import Budget, BudgetItem, ProformaInvoice
from app.domain.enums.budget_status import BudgetStatus
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from app.domain.repositories.budget_repository import IBudgetRepository
from app.infrastructure.supabase.ingestion_mappers import (
    map_budget,
    map_budget_item,
    map_proforma,
)
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


class SupabaseBudgetRepository(IBudgetRepository):
    BUDGETS = "budgets"
    BUDGET_ITEMS = "budget_items"
    PROFORMA = "proforma_invoices"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_by_id(self, budget_id: UUID) -> Budget | None:
        response = (
            self._client.table(self.BUDGETS).select("*").eq("id", str(budget_id)).limit(1).execute()
        )
        row = get_single_row(response)
        return map_budget(row) if row else None

    def find_by_project(self, project_id: UUID) -> list[Budget]:
        response = (
            self._client.table(self.BUDGETS)
            .select("*")
            .eq("project_id", str(project_id))
            .order("created_at", desc=True)
            .execute()
        )
        return [map_budget(r) for r in get_rows(response)]

    def find_by_verification_hash(self, verification_hash: str) -> Budget | None:
        response = (
            self._client.table(self.BUDGETS)
            .select("*")
            .eq("verification_hash", verification_hash)
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return map_budget(row) if row else None

    def has_approved_budget(self, project_id: UUID) -> bool:
        response = (
            self._client.table(self.BUDGETS)
            .select("id", count="exact")
            .eq("project_id", str(project_id))
            .eq("status", BudgetStatus.APPROVED.value)
            .execute()
        )
        return (response.count or 0) > 0

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
        payload = {
            "project_id": str(project_id),
            "budget_number": budget_number,
            "title": title,
            "total_amount": str(total_amount),
            "currency": currency,
            "verification_hash": verification_hash,
            "qr_code_data": qr_code_data,
            "qr_code_image": qr_code_image,
            "created_by": str(created_by),
            "status": BudgetStatus.DRAFT.value,
        }
        response = self._client.table(self.BUDGETS).insert(payload).execute()
        rows = get_rows(response)
        if not rows:
            raise RuntimeError("Falha ao criar orçamento")
        budget = map_budget(rows[0])

        if items:
            for item in items:
                item["budget_id"] = str(budget.id)
            self._client.table(self.BUDGET_ITEMS).insert(items).execute()

        return budget

    def get_budget_items(self, budget_id: UUID) -> list[BudgetItem]:
        response = (
            self._client.table(self.BUDGET_ITEMS)
            .select("*")
            .eq("budget_id", str(budget_id))
            .order("line_order", desc=False)
            .execute()
        )
        return [map_budget_item(r) for r in get_rows(response)]

    def approve_budget(self, budget_id: UUID, approved_by: UUID) -> Budget:
        payload = {
            "status": BudgetStatus.APPROVED.value,
            "approved_by": str(approved_by),
            "approved_at": datetime.now(timezone.utc).isoformat(),
        }
        response = (
            self._client.table(self.BUDGETS).update(payload).eq("id", str(budget_id)).execute()
        )
        rows = get_rows(response)
        if not rows:
            raise EntityNotFoundError("Orçamento", str(budget_id))
        return map_budget(rows[0])

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
        payload = {
            "budget_id": str(budget_id),
            "project_id": str(project_id),
            "invoice_number": invoice_number,
            "client_name": client_name,
            "client_tax_id": client_tax_id,
            "total_amount": str(total_amount),
            "currency": currency,
            "verification_hash": verification_hash,
            "notes": notes,
            "created_by": str(created_by),
        }
        if qr_code_data is not None:
            payload["qr_code_data"] = qr_code_data
        if qr_code_image is not None:
            payload["qr_code_image"] = qr_code_image
        response = self._client.table(self.PROFORMA).insert(payload).execute()
        rows = get_rows(response)
        if not rows:
            raise RuntimeError("Falha ao criar fatura proforma")
        return map_proforma(rows[0])

    def find_proforma_by_id(self, invoice_id: UUID) -> ProformaInvoice | None:
        response = (
            self._client.table(self.PROFORMA)
            .select("*")
            .eq("id", str(invoice_id))
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return map_proforma(row) if row else None

    def find_proformas_by_project(self, project_id: UUID) -> list[ProformaInvoice]:
        response = (
            self._client.table(self.PROFORMA)
            .select("*")
            .eq("project_id", str(project_id))
            .order("issued_at", desc=True)
            .execute()
        )
        return [map_proforma(r) for r in get_rows(response)]

    def next_budget_number(self) -> str:
        year = datetime.now(timezone.utc).year
        response = (
            self._client.table(self.BUDGETS)
            .select("budget_number")
            .like("budget_number", f"ORC-{year}-%")
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        rows = get_rows(response)
        if not rows:
            return f"ORC-{year}-0001"
        last = rows[0]["budget_number"].split("-")[-1]
        try:
            seq = int(last) + 1
        except ValueError:
            seq = 1
        return f"ORC-{year}-{seq:04d}"

    def next_invoice_number(self) -> str:
        """UC17 — Formato PF-{YYYY}-{XXXXX}."""
        year = datetime.now(timezone.utc).year
        response = (
            self._client.table(self.PROFORMA)
            .select("invoice_number")
            .like("invoice_number", f"PF-{year}-%")
            .order("issued_at", desc=True)
            .limit(1)
            .execute()
        )
        rows = get_rows(response)
        if not rows:
            return f"PF-{year}-00001"
        last = rows[0]["invoice_number"].split("-")[-1]
        try:
            seq = int(last) + 1
        except ValueError:
            seq = 1
        return f"PF-{year}-{seq:05d}"

    def delete_by_project(self, project_id: UUID) -> int:
        """Apaga proformas e orçamentos do projecto para libertar cost_items."""
        project_key = str(project_id)
        budgets = self.find_by_project(project_id)
        # proforma_invoices.budget_id → ON DELETE RESTRICT
        self._client.table(self.PROFORMA).delete().eq("project_id", project_key).execute()
        # budget_items.budget_id → ON DELETE CASCADE
        self._client.table(self.BUDGETS).delete().eq("project_id", project_key).execute()
        return len(budgets)

    def delete_budget_items_by_cost_item(self, cost_item_id: UUID) -> None:
        self._client.table(self.BUDGET_ITEMS).delete().eq(
            "cost_item_id", str(cost_item_id)
        ).execute()
