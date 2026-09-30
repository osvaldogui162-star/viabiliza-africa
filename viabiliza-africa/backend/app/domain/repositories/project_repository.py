from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.entities.project import Project
from app.domain.enums.country import Country
from app.domain.enums.currency import Currency
from app.domain.enums.project_sector import ProjectSector
from app.domain.enums.project_status import ProjectStatus


class ProjectFilters:
    """Value object para filtros de listagem (UC07)."""

    def __init__(
        self,
        *,
        status: ProjectStatus | None = None,
        country: Country | None = None,
        sector: ProjectSector | None = None,
        owner_id: UUID | None = None,
        shared_with_user_id: UUID | None = None,
        include_deleted: bool = False,
        search: str | None = None,
    ) -> None:
        self.status = status
        self.country = country
        self.sector = sector
        self.owner_id = owner_id
        self.shared_with_user_id = shared_with_user_id
        self.include_deleted = include_deleted
        self.search = search


class IProjectRepository(ABC):
    """Interface do repositório de projetos (Dependency Inversion)."""

    @abstractmethod
    def find_by_id(self, project_id: UUID, *, include_deleted: bool = False) -> Project | None:
        ...

    @abstractmethod
    def find_by_ids(
        self, project_ids: list[UUID], *, include_deleted: bool = False
    ) -> list[Project]:
        ...

    @abstractmethod
    def find_id_timestamps(
        self,
        filters: ProjectFilters,
        *,
        only_ids: list[UUID] | None = None,
    ) -> list[tuple[UUID, datetime]]:
        """Pares (id, created_at) para paginação leve."""
        ...

    @abstractmethod
    def find_all(
        self,
        filters: ProjectFilters,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Project]:
        ...

    @abstractmethod
    def count(self, filters: ProjectFilters) -> int:
        ...

    @abstractmethod
    def create(
        self,
        *,
        owner_id: UUID,
        name: str,
        description: str | None,
        company_name: str,
        company_tax_id: str | None,
        sector: ProjectSector,
        country: Country,
        currency: Currency,
        investment_amount: Decimal,
        project_horizon_years: int,
        discount_rate: Decimal | None,
        bank_code: str | None = None,
        bank_rate_label: str | None = None,
        bank_rate_source_url: str | None = None,
        rep_full_name: str | None = None,
        rep_email: str | None = None,
        rep_id_number: str | None = None,
        rep_phone: str | None = None,
        rep_role: str | None = None,
        company_province: str | None = None,
        company_municipality: str | None = None,
        company_address: str | None = None,
        company_activity: str | None = None,
        company_phone: str | None = None,
        company_email: str | None = None,
        company_website: str | None = None,
        company_latitude: Decimal | None = None,
        company_longitude: Decimal | None = None,
        geocode_verified: bool = False,
        geocode_source: str | None = None,
        financing_type: str | None = None,
        loan_term_months: int | None = None,
        bank_branch: str | None = None,
    ) -> Project:
        ...

    @abstractmethod
    def update(
        self,
        project_id: UUID,
        *,
        name: str | None = None,
        description: str | None = None,
        company_name: str | None = None,
        company_tax_id: str | None = None,
        sector: ProjectSector | None = None,
        country: Country | None = None,
        currency: Currency | None = None,
        investment_amount: Decimal | None = None,
        project_horizon_years: int | None = None,
        discount_rate: Decimal | None = None,
        status: ProjectStatus | None = None,
        bank_code: str | None = None,
        bank_rate_label: str | None = None,
        bank_rate_source_url: str | None = None,
        rep_full_name: str | None = None,
        rep_email: str | None = None,
        rep_id_number: str | None = None,
        rep_phone: str | None = None,
        rep_role: str | None = None,
        company_province: str | None = None,
        company_municipality: str | None = None,
        company_address: str | None = None,
        company_activity: str | None = None,
        company_phone: str | None = None,
        company_email: str | None = None,
        company_website: str | None = None,
        company_latitude: Decimal | None = None,
        company_longitude: Decimal | None = None,
        geocode_verified: bool | None = None,
        geocode_source: str | None = None,
        financing_type: str | None = None,
        loan_term_months: int | None = None,
        bank_branch: str | None = None,
    ) -> Project:
        ...

    @abstractmethod
    def soft_delete(self, project_id: UUID) -> Project:
        ...

    @abstractmethod
    def is_shared_with_user(self, project_id: UUID, user_id: UUID) -> bool:
        ...

    @abstractmethod
    def set_has_approved_budget(self, project_id: UUID, value: bool) -> None:
        ...

    @abstractmethod
    def update_strategic_insights(
        self,
        project_id: UUID,
        *,
        mission: str,
        vision: str,
        core_values: list,
        swot_analysis: dict,
        risk_register: list,
        aipex_incentives: list,
        strategic_generated_at: datetime,
    ) -> Project:
        ...
