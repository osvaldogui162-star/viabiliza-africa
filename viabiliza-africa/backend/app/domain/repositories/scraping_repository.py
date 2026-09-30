from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

from app.domain.entities.scraping import ScrapingJob, ScrapingResult
from app.domain.enums.scraping_job_status import ScrapingJobStatus


class IScrapingRepository(ABC):
    @abstractmethod
    def create_job(
        self,
        *,
        project_id: UUID,
        search_query: str,
        sources: list[str],
        created_by: UUID,
    ) -> ScrapingJob:
        ...

    @abstractmethod
    def update_job_status(
        self,
        job_id: UUID,
        *,
        status: ScrapingJobStatus,
        results_count: int = 0,
        error_message: str | None = None,
    ) -> ScrapingJob:
        ...

    @abstractmethod
    def find_job_by_id(self, job_id: UUID) -> ScrapingJob | None:
        ...

    @abstractmethod
    def find_jobs_by_project(self, project_id: UUID) -> list[ScrapingJob]:
        ...

    @abstractmethod
    def create_results(self, results: list[dict]) -> list[ScrapingResult]:
        ...

    @abstractmethod
    def find_results_by_job(self, job_id: UUID) -> list[ScrapingResult]:
        ...

    @abstractmethod
    def find_result_by_id(self, result_id: UUID) -> ScrapingResult | None:
        ...

    @abstractmethod
    def select_result(
        self, result_id: UUID, *, cost_item_id: UUID | None
    ) -> ScrapingResult:
        ...

    @abstractmethod
    def get_active_sources(self) -> list[dict]:
        ...
