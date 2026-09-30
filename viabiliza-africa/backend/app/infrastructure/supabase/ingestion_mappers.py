from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.entities.audit_trail_entry import AuditTrailEntry
from app.domain.entities.budget import Budget, BudgetItem, ProformaInvoice
from app.domain.entities.cost_item import CostItem
from app.domain.entities.scraping import ScrapingJob, ScrapingResult
from app.domain.enums.audit_action import AuditAction
from app.domain.enums.audit_entity_type import AuditEntityType
from app.domain.enums.budget_status import BudgetStatus
from app.domain.enums.cost_item_type import CostItemType
from app.domain.enums.currency import Currency
from app.domain.enums.data_source import DataSource
from app.domain.enums.scraping_job_status import ScrapingJobStatus


def _dt(value: str | None) -> datetime:
    if not value:
        return datetime.now()
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def map_cost_item(row: dict) -> CostItem:
    return CostItem(
        id=UUID(row["id"]),
        project_id=UUID(row["project_id"]),
        item_type=CostItemType(row["item_type"]),
        category=row["category"],
        description=row["description"],
        quantity=Decimal(str(row["quantity"])),
        unit=row["unit"],
        unit_price=Decimal(str(row["unit_price"])),
        total_amount=Decimal(str(row["total_amount"])),
        currency=Currency(row["currency"]),
        source=DataSource(row["source"]),
        data_hash=row["data_hash"],
        supplier_name=row.get("supplier_name"),
        supplier_nif=row.get("supplier_nif"),
        supplier_url=row.get("supplier_url"),
        scraping_result_id=UUID(row["scraping_result_id"]) if row.get("scraping_result_id") else None,
        metadata=row.get("metadata") or {},
        created_by=UUID(row["created_by"]),
        created_at=_dt(row.get("created_at")),
        updated_at=_dt(row.get("updated_at")),
    )


def map_scraping_job(row: dict) -> ScrapingJob:
    return ScrapingJob(
        id=UUID(row["id"]),
        project_id=UUID(row["project_id"]),
        search_query=row["search_query"],
        sources=row.get("sources") or [],
        status=ScrapingJobStatus(row["status"]),
        results_count=int(row.get("results_count", 0)),
        error_message=row.get("error_message"),
        created_by=UUID(row["created_by"]),
        created_at=_dt(row.get("created_at")),
        completed_at=_dt(row["completed_at"]) if row.get("completed_at") else None,
    )


def map_scraping_result(row: dict) -> ScrapingResult:
    return ScrapingResult(
        id=UUID(row["id"]),
        job_id=UUID(row["job_id"]),
        project_id=UUID(row["project_id"]),
        source=row["source"],
        supplier_name=row["supplier_name"],
        product_name=row["product_name"],
        price=Decimal(str(row["price"])),
        currency=row["currency"],
        product_url=row.get("product_url"),
        is_selected=bool(row.get("is_selected", False)),
        selected_for_item_id=(
            UUID(row["selected_for_item_id"]) if row.get("selected_for_item_id") else None
        ),
        data_hash=row["data_hash"],
        scraped_at=_dt(row.get("scraped_at")),
    )


def map_budget(row: dict) -> Budget:
    return Budget(
        id=UUID(row["id"]),
        project_id=UUID(row["project_id"]),
        budget_number=row["budget_number"],
        title=row["title"],
        total_amount=Decimal(str(row["total_amount"])),
        currency=row["currency"],
        status=BudgetStatus(row["status"]),
        verification_hash=row["verification_hash"],
        qr_code_data=row["qr_code_data"],
        qr_code_image=row["qr_code_image"],
        created_by=UUID(row["created_by"]),
        approved_by=UUID(row["approved_by"]) if row.get("approved_by") else None,
        approved_at=_dt(row["approved_at"]) if row.get("approved_at") else None,
        created_at=_dt(row.get("created_at")),
        updated_at=_dt(row.get("updated_at")),
    )


def map_budget_item(row: dict) -> BudgetItem:
    return BudgetItem(
        id=UUID(row["id"]),
        budget_id=UUID(row["budget_id"]),
        cost_item_id=UUID(row["cost_item_id"]),
        item_type=CostItemType(row["item_type"]),
        category=row["category"],
        description=row["description"],
        quantity=Decimal(str(row["quantity"])),
        unit=row["unit"],
        unit_price=Decimal(str(row["unit_price"])),
        total_amount=Decimal(str(row["total_amount"])),
        item_hash=row["item_hash"],
        supplier_name=row.get("supplier_name"),
        line_order=int(row.get("line_order", 0)),
    )


def map_proforma(row: dict) -> ProformaInvoice:
    return ProformaInvoice(
        id=UUID(row["id"]),
        budget_id=UUID(row["budget_id"]),
        project_id=UUID(row["project_id"]),
        invoice_number=row["invoice_number"],
        client_name=row["client_name"],
        client_tax_id=row.get("client_tax_id"),
        total_amount=Decimal(str(row["total_amount"])),
        currency=row["currency"],
        verification_hash=row["verification_hash"],
        notes=row.get("notes"),
        created_by=UUID(row["created_by"]),
        issued_at=_dt(row.get("issued_at")),
        qr_code_data=row.get("qr_code_data"),
        qr_code_image=row.get("qr_code_image"),
    )


def map_audit_trail(row: dict) -> AuditTrailEntry:
    return AuditTrailEntry(
        id=UUID(row["id"]),
        project_id=UUID(row["project_id"]),
        entity_type=AuditEntityType(row["entity_type"]),
        entity_id=UUID(row["entity_id"]),
        action=AuditAction(row["action"]),
        actor_id=UUID(row["actor_id"]) if row.get("actor_id") else None,
        data_hash=row["data_hash"],
        previous_hash=row.get("previous_hash"),
        ip_address=row.get("ip_address"),
        metadata=row.get("metadata") or {},
        created_at=_dt(row.get("created_at")),
    )
