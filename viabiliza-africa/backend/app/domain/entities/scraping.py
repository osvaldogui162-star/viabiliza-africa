from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.enums.scraping_job_status import ScrapingJobStatus


@dataclass
class ScrapingJob:
    id: UUID
    project_id: UUID
    search_query: str
    sources: list[str]
    status: ScrapingJobStatus
    results_count: int
    error_message: str | None
    created_by: UUID
    created_at: datetime
    completed_at: datetime | None


@dataclass
class ScrapingResult:
    id: UUID
    job_id: UUID
    project_id: UUID
    source: str
    supplier_name: str
    product_name: str
    price: Decimal
    currency: str
    product_url: str | None
    is_selected: bool
    selected_for_item_id: UUID | None
    data_hash: str
    scraped_at: datetime
