from datetime import datetime, timezone
from uuid import UUID

from supabase import Client

from app.domain.entities.scraping import ScrapingJob, ScrapingResult
from app.domain.enums.scraping_job_status import ScrapingJobStatus
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from app.domain.repositories.scraping_repository import IScrapingRepository
from app.infrastructure.supabase.ingestion_mappers import map_scraping_job, map_scraping_result
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


class SupabaseScrapingRepository(IScrapingRepository):
    JOBS = "scraping_jobs"
    RESULTS = "scraping_results"
    SOURCES = "scraping_sources"

    def __init__(self, client: Client) -> None:
        self._client = client

    def create_job(
        self,
        *,
        project_id: UUID,
        search_query: str,
        sources: list[str],
        created_by: UUID,
    ) -> ScrapingJob:
        payload = {
            "project_id": str(project_id),
            "search_query": search_query,
            "sources": sources,
            "status": ScrapingJobStatus.PENDING.value,
            "created_by": str(created_by),
        }
        response = self._client.table(self.JOBS).insert(payload).execute()
        rows = get_rows(response)
        if not rows:
            raise RuntimeError("Falha ao criar job de scraping")
        return map_scraping_job(rows[0])

    def update_job_status(
        self,
        job_id: UUID,
        *,
        status: ScrapingJobStatus,
        results_count: int = 0,
        error_message: str | None = None,
    ) -> ScrapingJob:
        payload: dict = {
            "status": status.value,
            "results_count": results_count,
            "error_message": error_message,
        }
        if status in (ScrapingJobStatus.COMPLETED, ScrapingJobStatus.FAILED):
            payload["completed_at"] = datetime.now(timezone.utc).isoformat()

        response = (
            self._client.table(self.JOBS).update(payload).eq("id", str(job_id)).execute()
        )
        rows = get_rows(response)
        if not rows:
            raise EntityNotFoundError("Job de scraping", str(job_id))
        return map_scraping_job(rows[0])

    def find_job_by_id(self, job_id: UUID) -> ScrapingJob | None:
        response = (
            self._client.table(self.JOBS).select("*").eq("id", str(job_id)).limit(1).execute()
        )
        row = get_single_row(response)
        return map_scraping_job(row) if row else None

    def find_jobs_by_project(self, project_id: UUID) -> list[ScrapingJob]:
        response = (
            self._client.table(self.JOBS)
            .select("*")
            .eq("project_id", str(project_id))
            .order("created_at", desc=True)
            .execute()
        )
        return [map_scraping_job(r) for r in get_rows(response)]

    def create_results(self, results: list[dict]) -> list[ScrapingResult]:
        if not results:
            return []
        response = self._client.table(self.RESULTS).insert(results).execute()
        return [map_scraping_result(r) for r in get_rows(response)]

    def find_results_by_job(self, job_id: UUID) -> list[ScrapingResult]:
        response = (
            self._client.table(self.RESULTS)
            .select("*")
            .eq("job_id", str(job_id))
            .order("price", desc=False)
            .execute()
        )
        return [map_scraping_result(r) for r in get_rows(response)]

    def find_result_by_id(self, result_id: UUID) -> ScrapingResult | None:
        response = (
            self._client.table(self.RESULTS)
            .select("*")
            .eq("id", str(result_id))
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return map_scraping_result(row) if row else None

    def select_result(self, result_id: UUID, *, cost_item_id: UUID | None) -> ScrapingResult:
        payload = {
            "is_selected": True,
            "selected_for_item_id": str(cost_item_id) if cost_item_id else None,
        }
        response = (
            self._client.table(self.RESULTS).update(payload).eq("id", str(result_id)).execute()
        )
        rows = get_rows(response)
        if not rows:
            raise EntityNotFoundError("Resultado de scraping", str(result_id))
        return map_scraping_result(rows[0])

    def get_active_sources(self) -> list[dict]:
        try:
            response = (
                self._client.table(self.SOURCES)
                .select(
                    "id, code, name, base_url, is_active, categories, scrape_enabled, city_note"
                )
                .eq("is_active", True)
                .execute()
            )
            rows = get_rows(response)
        except Exception:
            response = (
                self._client.table(self.SOURCES)
                .select("id, code, name, base_url, is_active")
                .eq("is_active", True)
                .execute()
            )
            rows = get_rows(response)

        # Garantir retalhistas do catálogo domain mesmo antes da migration 014
        from app.domain.catalog.angolan_retail_suppliers import ALL_RETAIL_SUPPLIERS

        by_code = {r["code"]: r for r in rows}
        for supplier in ALL_RETAIL_SUPPLIERS:
            if supplier.code not in by_code:
                by_code[supplier.code] = {
                    "id": None,
                    "code": supplier.code,
                    "name": supplier.name,
                    "base_url": supplier.base_url,
                    "is_active": True,
                    "categories": list(supplier.groups),
                    "scrape_enabled": supplier.scrape_enabled,
                    "city_note": supplier.city_note,
                }
            else:
                row = by_code[supplier.code]
                row.setdefault("categories", list(supplier.groups))
                row.setdefault("scrape_enabled", supplier.scrape_enabled)
                row.setdefault("city_note", supplier.city_note)
        return list(by_code.values())
