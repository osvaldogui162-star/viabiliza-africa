from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.enums.country import Country
from app.domain.enums.currency import Currency
from app.domain.enums.project_sector import ProjectSector
from app.domain.enums.project_status import ProjectStatus


@dataclass
class Project:
    """Entidade de domínio — projeto de estudo de viabilidade."""

    id: UUID
    owner_id: UUID
    name: str
    description: str | None
    company_name: str
    company_tax_id: str | None
    sector: ProjectSector
    country: Country
    currency: Currency
    investment_amount: Decimal
    project_horizon_years: int
    discount_rate: Decimal | None
    status: ProjectStatus
    has_approved_budget: bool
    deleted_at: datetime | None
    created_at: datetime
    updated_at: datetime
    bank_code: str | None = None
    bank_rate_label: str | None = None
    bank_rate_source_url: str | None = None
    rep_full_name: str | None = None
    rep_email: str | None = None
    rep_id_number: str | None = None
    rep_phone: str | None = None
    rep_role: str | None = None
    company_province: str | None = None
    company_municipality: str | None = None
    company_address: str | None = None
    company_activity: str | None = None
    company_phone: str | None = None
    company_email: str | None = None
    company_website: str | None = None
    company_latitude: Decimal | None = None
    company_longitude: Decimal | None = None
    geocode_verified: bool = False
    geocode_source: str | None = None
    financing_type: str | None = None
    loan_term_months: int | None = None
    bank_branch: str | None = None
    mission: str | None = None
    vision: str | None = None
    core_values: list | None = None
    swot_analysis: dict | None = None
    risk_register: list | None = None
    aipex_incentives: list | None = None
    strategic_generated_at: datetime | None = None

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def is_editable(self) -> bool:
        return not self.is_deleted and self.status.is_editable()

    def can_be_deleted(self) -> bool:
        return not self.is_deleted and not self.has_approved_budget
