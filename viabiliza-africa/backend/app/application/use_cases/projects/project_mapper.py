from decimal import Decimal
from uuid import UUID

from app.application.dto.project_dto import OwnerSummary, ProjectOutput, ProjectShareOutput
from app.domain.catalog.angola_admin_divisions import resolve_location
from app.domain.entities.cost_item import CostItem
from app.domain.entities.project import Project
from app.domain.entities.project_share import ProjectShare
from app.domain.entities.user import User
from app.domain.enums.cost_item_type import CostItemType
from app.domain.enums.financing_type import FinancingType
from app.domain.enums.project_sector import ProjectSector


def _format_decimal(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return format(value, "f")


def summarize_project_spend(items: list[CostItem]) -> tuple[Decimal, Decimal, Decimal]:
    """Devolve (gasto_total, capex, opex) a partir dos cost items."""
    spent = Decimal("0")
    capex = Decimal("0")
    opex = Decimal("0")
    for item in items:
        total = Decimal(str(item.total_amount or 0))
        spent += total
        if item.item_type == CostItemType.CAPEX:
            capex += total
        else:
            opex += total
    return spent, capex, opex


def to_project_output(
    project: Project,
    *,
    owner: User | None = None,
    actor_id: UUID | None = None,
    is_shared: bool = False,
    shares_count: int = 0,
    cost_items: list[CostItem] | None = None,
    spend_summary: tuple[Decimal, Decimal, Decimal] | None = None,
    my_access: dict | None = None,
) -> ProjectOutput:
    owner_summary = None
    if owner:
        owner_summary = OwnerSummary(
            id=owner.id,
            email=owner.email,
            full_name=owner.full_name,
        )

    if spend_summary is not None:
        spent, capex, opex = spend_summary
    else:
        spent, capex, opex = summarize_project_spend(cost_items or [])
    investment = Decimal(str(project.investment_amount or 0))
    remaining = investment - spent

    province_label = None
    municipality_label = None
    if project.company_province and project.company_municipality:
        resolved = resolve_location(project.company_province, project.company_municipality)
        if resolved:
            municipality, province = resolved
            province_label = province.label
            municipality_label = municipality.label

    financing_label = None
    if project.financing_type:
        try:
            financing_label = FinancingType(project.financing_type).label_pt
        except ValueError:
            financing_label = project.financing_type

    return ProjectOutput(
        id=project.id,
        owner_id=project.owner_id,
        owner=owner_summary,
        name=project.name,
        description=project.description,
        company_name=project.company_name,
        company_tax_id=project.company_tax_id,
        sector=project.sector.value,
        sector_label=project.sector.label_pt,
        country=project.country.value,
        country_label=project.country.label_pt,
        currency=project.currency.value,
        investment_amount=_format_decimal(project.investment_amount) or "0",
        project_horizon_years=project.project_horizon_years,
        discount_rate=_format_decimal(project.discount_rate),
        status=project.status.value,
        status_label=project.status.label_pt,
        has_approved_budget=project.has_approved_budget,
        is_owner=actor_id == project.owner_id if actor_id else False,
        is_shared=is_shared,
        shares_count=shares_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
        bank_code=project.bank_code,
        bank_rate_label=project.bank_rate_label,
        bank_rate_source_url=project.bank_rate_source_url,
        rep_full_name=project.rep_full_name,
        rep_email=project.rep_email,
        rep_id_number=project.rep_id_number,
        rep_phone=project.rep_phone,
        rep_role=project.rep_role,
        company_province=project.company_province,
        company_province_label=province_label,
        company_municipality=project.company_municipality,
        company_municipality_label=municipality_label,
        company_address=project.company_address,
        company_activity=project.company_activity,
        company_phone=project.company_phone,
        company_email=project.company_email,
        company_website=project.company_website,
        company_latitude=_format_decimal(project.company_latitude),
        company_longitude=_format_decimal(project.company_longitude),
        geocode_verified=project.geocode_verified,
        geocode_source=project.geocode_source,
        financing_type=project.financing_type,
        financing_type_label=financing_label,
        loan_term_months=project.loan_term_months,
        bank_branch=project.bank_branch,
        spent_total=format(spent.quantize(Decimal("0.01")), "f"),
        remaining_balance=format(remaining.quantize(Decimal("0.01")), "f"),
        capex_spent=format(capex.quantize(Decimal("0.01")), "f"),
        opex_spent=format(opex.quantize(Decimal("0.01")), "f"),
        mission=project.mission,
        vision=project.vision,
        core_values=project.core_values or [],
        swot_analysis=project.swot_analysis or {},
        risk_register=project.risk_register or [],
        aipex_incentives=project.aipex_incentives or [],
        strategic_generated_at=project.strategic_generated_at,
        my_access=my_access,
    )


def to_share_output(
    share: ProjectShare,
    *,
    user: User,
    shared_by_user: User,
) -> ProjectShareOutput:
    return ProjectShareOutput(
        id=share.id,
        project_id=share.project_id,
        user_id=share.user_id,
        user_email=user.email,
        user_full_name=user.full_name,
        user_role=user.role.value,
        shared_by=share.shared_by,
        shared_by_name=shared_by_user.full_name,
        permission=share.permission.value,
        job_title=share.job_title,
        office_member_id=share.office_member_id,
        capabilities=share.capabilities or {},
        effective_capabilities=share.effective_capabilities(),
        created_at=share.created_at,
    )
