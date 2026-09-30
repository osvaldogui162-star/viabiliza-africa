from app.application.dto.ingestion_dto import (
    AuditTrailOutput,
    BudgetOutput,
    CostItemOutput,
    ProformaOutput,
    ScrapingJobOutput,
    ScrapingResultOutput,
)
from app.domain.catalog.angolan_retail_suppliers import suppliers_by_code
from app.domain.entities.audit_trail_entry import AuditTrailEntry
from app.domain.entities.budget import Budget, ProformaInvoice
from app.domain.entities.cost_item import CostItem
from app.domain.entities.scraping import ScrapingJob, ScrapingResult
from app.infrastructure.scraping.supplier_contacts import resolve_contacts_for_cost_item

_CHANNEL_LABELS = {
    "manual": "Manual",
    "excel": "Excel",
    "scraping": "Scraping",
}

_MARKETPLACE_LABELS = {
    "jumia": "Jumia Angola",
    "jiji": "Jiji Angola",
    "kikolo": "Kikolo Online",
    "socia": "Socia.ao",
    "praca_digital": "Praça Digital",
    "facebook_marketplace": "Facebook Marketplace",
    "referencia_sectorial": "Referência setorial",
}


def label_for_price_source(
    code: str | None,
    *,
    supplier_name: str | None = None,
    channel: str | None = None,
) -> str:
    """Converte código de origem (jumia, ovarmat, …) em nome legível."""
    if code and isinstance(code, str) and code.strip():
        key = code.strip()
        if key in _MARKETPLACE_LABELS:
            return _MARKETPLACE_LABELS[key]
        retail = suppliers_by_code().get(key)
        if retail:
            return retail.name
        return key.replace("_", " ").strip().title()

    if supplier_name and supplier_name.strip():
        return supplier_name.strip()

    if channel:
        return _CHANNEL_LABELS.get(channel, channel)
    return "Desconhecida"


def resolve_cost_item_source_label(item: CostItem) -> str:
    """Rótulo legível da origem do preço (marketplace/retalhista), não só o canal."""
    meta = item.metadata or {}
    display = meta.get("source_display")
    if isinstance(display, str) and display.strip():
        return display.strip()

    raw = meta.get("price_source") or meta.get("scraping_source")
    if isinstance(raw, str) and raw.strip():
        return label_for_price_source(raw, supplier_name=item.supplier_name)

    if item.supplier_name and item.supplier_name.strip():
        # Auto-ingestão / scraping com fornecedor mas sem código de fonte
        if meta.get("auto_ingestion") or item.source.value == "scraping":
            return item.supplier_name.strip()

    return _CHANNEL_LABELS.get(item.source.value, item.source.value)


def to_cost_item_output(item: CostItem) -> CostItemOutput:
    return CostItemOutput(
        id=item.id,
        project_id=item.project_id,
        item_type=item.item_type.value,
        category=item.category,
        description=item.description,
        quantity=format(item.quantity, "f"),
        unit=item.unit,
        unit_price=format(item.unit_price, "f"),
        total_amount=format(item.total_amount, "f"),
        currency=item.currency.value,
        source=item.source.value,
        source_label=resolve_cost_item_source_label(item),
        data_hash=item.data_hash,
        supplier_name=item.supplier_name,
        supplier_nif=item.supplier_nif,
        supplier_url=item.supplier_url,
        contacts=resolve_contacts_for_cost_item(item),
        metadata=item.metadata or {},
        created_at=item.created_at,
    )


def to_scraping_source_output(row: dict) -> dict:
    return {
        "id": str(row.get("id", "")),
        "code": row["code"],
        "name": row["name"],
        "base_url": row["base_url"],
        "is_active": row.get("is_active", True),
        "categories": row.get("categories") or [],
        "scrape_enabled": bool(row.get("scrape_enabled", False)),
        "city_note": row.get("city_note"),
    }


def to_scraping_job_output(job: ScrapingJob) -> ScrapingJobOutput:
    return ScrapingJobOutput(
        id=job.id,
        project_id=job.project_id,
        search_query=job.search_query,
        sources=job.sources,
        status=job.status.value,
        results_count=job.results_count,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )


def to_scraping_result_output(result: ScrapingResult) -> ScrapingResultOutput:
    return ScrapingResultOutput(
        id=result.id,
        job_id=result.job_id,
        source=result.source,
        supplier_name=result.supplier_name,
        product_name=result.product_name,
        price=format(result.price, "f"),
        currency=result.currency,
        product_url=result.product_url,
        is_selected=result.is_selected,
        data_hash=result.data_hash,
    )


def to_budget_output(budget: Budget, *, items_count: int = 0) -> BudgetOutput:
    return BudgetOutput(
        id=budget.id,
        project_id=budget.project_id,
        budget_number=budget.budget_number,
        title=budget.title,
        total_amount=format(budget.total_amount, "f"),
        currency=budget.currency,
        status=budget.status.value,
        verification_hash=budget.verification_hash,
        qr_code_data=budget.qr_code_data,
        qr_code_image=budget.qr_code_image,
        items_count=items_count,
        approved_at=budget.approved_at,
        created_at=budget.created_at,
    )


def to_proforma_output(invoice: ProformaInvoice) -> ProformaOutput:
    return ProformaOutput(
        id=invoice.id,
        budget_id=invoice.budget_id,
        project_id=invoice.project_id,
        invoice_number=invoice.invoice_number,
        client_name=invoice.client_name,
        client_tax_id=invoice.client_tax_id,
        total_amount=format(invoice.total_amount, "f"),
        currency=invoice.currency,
        verification_hash=invoice.verification_hash,
        issued_at=invoice.issued_at,
        qr_code_data=invoice.qr_code_data,
        qr_code_image=invoice.qr_code_image,
    )


def to_audit_output(entry: AuditTrailEntry) -> AuditTrailOutput:
    return AuditTrailOutput(
        id=entry.id,
        project_id=entry.project_id,
        entity_type=entry.entity_type.value,
        entity_id=entry.entity_id,
        action=entry.action.value,
        actor_id=entry.actor_id,
        data_hash=entry.data_hash,
        previous_hash=entry.previous_hash,
        metadata=entry.metadata,
        created_at=entry.created_at,
    )
