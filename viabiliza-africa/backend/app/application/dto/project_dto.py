from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class CreateProjectInput:
    actor_id: UUID
    name: str
    description: str | None
    company_name: str
    company_tax_id: str | None
    sector: str
    country: str
    currency: str
    investment_amount: Decimal
    project_horizon_years: int
    discount_rate: Decimal | None
    ip_address: str | None = None
    user_agent: str | None = None
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


@dataclass(frozen=True)
class UpdateProjectInput:
    actor_id: UUID
    project_id: UUID
    name: str | None = None
    description: str | None = None
    company_name: str | None = None
    company_tax_id: str | None = None
    sector: str | None = None
    country: str | None = None
    currency: str | None = None
    investment_amount: Decimal | None = None
    project_horizon_years: int | None = None
    discount_rate: Decimal | None = None
    ip_address: str | None = None
    user_agent: str | None = None
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
    geocode_verified: bool | None = None
    geocode_source: str | None = None
    financing_type: str | None = None
    loan_term_months: int | None = None
    bank_branch: str | None = None


@dataclass(frozen=True)
class ListProjectsInput:
    actor_id: UUID
    status: str | None = None
    country: str | None = None
    sector: str | None = None
    search: str | None = None
    limit: int = 20
    offset: int = 0


@dataclass(frozen=True)
class ShareProjectInput:
    actor_id: UUID
    project_id: UUID
    user_email: str
    permission: str = "view"
    ip_address: str | None = None
    user_agent: str | None = None
    capabilities: dict | None = None
    office_member_id: UUID | None = None
    job_title: str | None = None


@dataclass(frozen=True)
class ShareProjectResult:
    share: "ProjectShareOutput | None" = None
    pending_invite: bool = False
    invite_email: str | None = None
    message: str | None = None
    expires_at: datetime | None = None


@dataclass(frozen=True)
class RemoveProjectShareInput:
    actor_id: UUID
    project_id: UUID
    target_user_id: UUID
    ip_address: str | None = None
    user_agent: str | None = None


@dataclass(frozen=True)
class OwnerSummary:
    id: UUID
    email: str
    full_name: str


@dataclass(frozen=True)
class ProjectOutput:
    id: UUID
    owner_id: UUID
    owner: OwnerSummary | None
    name: str
    description: str | None
    company_name: str
    company_tax_id: str | None
    sector: str
    sector_label: str
    country: str
    country_label: str
    currency: str
    investment_amount: str
    project_horizon_years: int
    discount_rate: str | None
    status: str
    status_label: str
    has_approved_budget: bool
    is_owner: bool
    is_shared: bool
    shares_count: int
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
    company_province_label: str | None = None
    company_municipality: str | None = None
    company_municipality_label: str | None = None
    company_address: str | None = None
    company_activity: str | None = None
    company_phone: str | None = None
    company_email: str | None = None
    company_website: str | None = None
    company_latitude: str | None = None
    company_longitude: str | None = None
    geocode_verified: bool = False
    geocode_source: str | None = None
    financing_type: str | None = None
    financing_type_label: str | None = None
    loan_term_months: int | None = None
    bank_branch: str | None = None
    # Saldo automático: investimento inicial − saídas (cost items)
    spent_total: str = "0"
    remaining_balance: str = "0"
    capex_spent: str = "0"
    opex_spent: str = "0"
    mission: str | None = None
    vision: str | None = None
    core_values: list | None = None
    swot_analysis: dict | None = None
    risk_register: list | None = None
    aipex_incentives: list | None = None
    strategic_generated_at: datetime | None = None
    my_access: dict | None = None


@dataclass(frozen=True)
class ProjectShareOutput:
    id: UUID
    project_id: UUID
    user_id: UUID
    user_email: str
    user_full_name: str
    user_role: str
    shared_by: UUID
    shared_by_name: str
    permission: str
    job_title: str | None
    office_member_id: UUID | None
    capabilities: dict[str, bool]
    effective_capabilities: dict[str, bool]
    created_at: datetime


@dataclass(frozen=True)
class ProjectDetailOutput:
    project: ProjectOutput
    shares: list[ProjectShareOutput]
