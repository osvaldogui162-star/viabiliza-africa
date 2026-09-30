from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.entities.project import Project
from app.domain.entities.project_share import ProjectShare
from app.domain.enums.country import Country
from app.domain.enums.currency import Currency
from app.domain.enums.project_sector import ProjectSector
from app.domain.enums.project_status import ProjectStatus
from app.domain.enums.share_permission import SharePermission


def _parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now()
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def map_project_row(row: dict) -> Project:
    return Project(
        id=UUID(row["id"]),
        owner_id=UUID(row["owner_id"]),
        name=row["name"],
        description=row.get("description"),
        company_name=row["company_name"],
        company_tax_id=row.get("company_tax_id"),
        sector=ProjectSector(row["sector"]),
        country=Country(row["country"]),
        currency=Currency(row["currency"]),
        investment_amount=Decimal(str(row["investment_amount"])),
        project_horizon_years=int(row["project_horizon_years"]),
        discount_rate=(
            Decimal(str(row["discount_rate"])) if row.get("discount_rate") is not None else None
        ),
        status=ProjectStatus(row["status"]),
        has_approved_budget=bool(row.get("has_approved_budget", False)),
        deleted_at=_parse_datetime(row["deleted_at"]) if row.get("deleted_at") else None,
        created_at=_parse_datetime(row.get("created_at")),
        updated_at=_parse_datetime(row.get("updated_at")),
        bank_code=row.get("bank_code"),
        bank_rate_label=row.get("bank_rate_label"),
        bank_rate_source_url=row.get("bank_rate_source_url"),
        rep_full_name=row.get("rep_full_name"),
        rep_email=row.get("rep_email"),
        rep_id_number=row.get("rep_id_number"),
        rep_phone=row.get("rep_phone"),
        rep_role=row.get("rep_role"),
        company_province=row.get("company_province"),
        company_municipality=row.get("company_municipality"),
        company_address=row.get("company_address"),
        company_activity=row.get("company_activity"),
        company_phone=row.get("company_phone"),
        company_email=row.get("company_email"),
        company_website=row.get("company_website"),
        company_latitude=(
            Decimal(str(row["company_latitude"]))
            if row.get("company_latitude") is not None
            else None
        ),
        company_longitude=(
            Decimal(str(row["company_longitude"]))
            if row.get("company_longitude") is not None
            else None
        ),
        geocode_verified=bool(row.get("geocode_verified", False)),
        geocode_source=row.get("geocode_source"),
        financing_type=row.get("financing_type"),
        loan_term_months=(
            int(row["loan_term_months"]) if row.get("loan_term_months") is not None else None
        ),
        bank_branch=row.get("bank_branch"),
        mission=row.get("mission"),
        vision=row.get("vision"),
        core_values=row.get("core_values") or [],
        swot_analysis=row.get("swot_analysis") or {},
        risk_register=row.get("risk_register") or [],
        aipex_incentives=row.get("aipex_incentives") or [],
        strategic_generated_at=(
            _parse_datetime(row["strategic_generated_at"])
            if row.get("strategic_generated_at")
            else None
        ),
    )


def map_project_share_row(row: dict) -> ProjectShare:
    caps = row.get("capabilities") or {}
    if not isinstance(caps, dict):
        caps = {}
    return ProjectShare(
        id=UUID(row["id"]),
        project_id=UUID(row["project_id"]),
        user_id=UUID(row["user_id"]),
        shared_by=UUID(row["shared_by"]),
        permission=SharePermission(row["permission"]),
        office_member_id=UUID(row["office_member_id"]) if row.get("office_member_id") else None,
        job_title=row.get("job_title"),
        capabilities={k: bool(v) for k, v in caps.items()},
        created_at=_parse_datetime(row.get("created_at")),
    )
