from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from supabase import Client

from app.domain.entities.project import Project
from app.domain.enums.country import Country
from app.domain.enums.currency import Currency
from app.domain.enums.project_sector import ProjectSector
from app.domain.enums.project_status import ProjectStatus
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from app.domain.repositories.project_repository import IProjectRepository, ProjectFilters
from app.infrastructure.supabase.project_mappers import map_project_row
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


def _extended_payload(
    *,
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
) -> dict:
    payload: dict = {}
    fields = {
        "rep_full_name": rep_full_name,
        "rep_email": rep_email,
        "rep_id_number": rep_id_number,
        "rep_phone": rep_phone,
        "rep_role": rep_role,
        "company_province": company_province,
        "company_municipality": company_municipality,
        "company_address": company_address,
        "company_activity": company_activity,
        "company_phone": company_phone,
        "company_email": company_email,
        "company_website": company_website,
        "geocode_source": geocode_source,
        "financing_type": financing_type,
        "loan_term_months": loan_term_months,
        "bank_branch": bank_branch,
    }
    for key, value in fields.items():
        if value is not None:
            payload[key] = value
    if company_latitude is not None:
        payload["company_latitude"] = str(company_latitude)
    if company_longitude is not None:
        payload["company_longitude"] = str(company_longitude)
    if geocode_verified is not None:
        payload["geocode_verified"] = geocode_verified
    return payload


class SupabaseProjectRepository(IProjectRepository):
    """Implementação Supabase do repositório de projetos."""

    TABLE = "projects"
    SHARES_TABLE = "project_shares"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_by_id(self, project_id: UUID, *, include_deleted: bool = False) -> Project | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("id", str(project_id))
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        if row is None:
            return None
        project = map_project_row(row)
        if project.is_deleted and not include_deleted:
            return None
        return project

    def find_by_ids(
        self, project_ids: list[UUID], *, include_deleted: bool = False
    ) -> list[Project]:
        if not project_ids:
            return []
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .in_("id", [str(pid) for pid in project_ids])
            .execute()
        )
        projects: list[Project] = []
        for row in get_rows(response):
            project = map_project_row(row)
            if project.is_deleted and not include_deleted:
                continue
            projects.append(project)
        return projects

    def find_id_timestamps(
        self,
        filters: ProjectFilters,
        *,
        only_ids: list[UUID] | None = None,
    ) -> list[tuple[UUID, datetime]]:
        query = self._client.table(self.TABLE).select("id,created_at")
        if not filters.include_deleted:
            query = query.is_("deleted_at", "null")
        if filters.status is not None:
            query = query.eq("status", filters.status.value)
        if filters.country is not None:
            query = query.eq("country", filters.country.value)
        if filters.sector is not None:
            query = query.eq("sector", filters.sector.value)
        if filters.owner_id is not None:
            query = query.eq("owner_id", str(filters.owner_id))
        if filters.search:
            term = filters.search.strip()
            query = query.or_(f"name.ilike.%{term}%,company_name.ilike.%{term}%")
        if only_ids:
            query = query.in_("id", [str(pid) for pid in only_ids])
        response = query.order("created_at", desc=True).limit(2000).execute()
        out: list[tuple[UUID, datetime]] = []
        for row in get_rows(response):
            created_raw = row.get("created_at")
            if not created_raw:
                continue
            created = datetime.fromisoformat(str(created_raw).replace("Z", "+00:00"))
            out.append((UUID(str(row["id"])), created))
        return out

    def find_all(
        self,
        filters: ProjectFilters,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Project]:
        query = self._client.table(self.TABLE).select("*")

        if not filters.include_deleted:
            query = query.is_("deleted_at", "null")
        if filters.status is not None:
            query = query.eq("status", filters.status.value)
        if filters.country is not None:
            query = query.eq("country", filters.country.value)
        if filters.sector is not None:
            query = query.eq("sector", filters.sector.value)
        if filters.owner_id is not None:
            query = query.eq("owner_id", str(filters.owner_id))
        if filters.search:
            term = filters.search.strip()
            query = query.or_(f"name.ilike.%{term}%,company_name.ilike.%{term}%")

        response = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
        return [map_project_row(row) for row in get_rows(response)]

    def count(self, filters: ProjectFilters) -> int:
        query = self._client.table(self.TABLE).select("id", count="exact")

        if not filters.include_deleted:
            query = query.is_("deleted_at", "null")
        if filters.status is not None:
            query = query.eq("status", filters.status.value)
        if filters.country is not None:
            query = query.eq("country", filters.country.value)
        if filters.sector is not None:
            query = query.eq("sector", filters.sector.value)
        if filters.owner_id is not None:
            query = query.eq("owner_id", str(filters.owner_id))
        if filters.search:
            term = filters.search.strip()
            query = query.or_(f"name.ilike.%{term}%,company_name.ilike.%{term}%")

        response = query.execute()
        return response.count or 0

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
        payload = {
            "owner_id": str(owner_id),
            "name": name,
            "description": description,
            "company_name": company_name,
            "company_tax_id": company_tax_id,
            "sector": sector.value,
            "country": country.value,
            "currency": currency.value,
            "investment_amount": str(investment_amount),
            "project_horizon_years": project_horizon_years,
            "discount_rate": str(discount_rate) if discount_rate is not None else None,
            "status": ProjectStatus.DRAFT.value,
            "has_approved_budget": False,
            "bank_code": bank_code,
            "bank_rate_label": bank_rate_label,
            "bank_rate_source_url": bank_rate_source_url,
            **_extended_payload(
                rep_full_name=rep_full_name,
                rep_email=rep_email,
                rep_id_number=rep_id_number,
                rep_phone=rep_phone,
                rep_role=rep_role,
                company_province=company_province,
                company_municipality=company_municipality,
                company_address=company_address,
                company_activity=company_activity,
                company_phone=company_phone,
                company_email=company_email,
                company_website=company_website,
                company_latitude=company_latitude,
                company_longitude=company_longitude,
                geocode_verified=geocode_verified,
                geocode_source=geocode_source,
                financing_type=financing_type,
                loan_term_months=loan_term_months,
                bank_branch=bank_branch,
            ),
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        rows = get_rows(response)
        if not rows:
            raise RuntimeError("Falha ao criar projeto")
        return map_project_row(rows[0])

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
        payload: dict = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if company_name is not None:
            payload["company_name"] = company_name
        if company_tax_id is not None:
            payload["company_tax_id"] = company_tax_id
        if sector is not None:
            payload["sector"] = sector.value
        if country is not None:
            payload["country"] = country.value
        if currency is not None:
            payload["currency"] = currency.value
        if investment_amount is not None:
            payload["investment_amount"] = str(investment_amount)
        if project_horizon_years is not None:
            payload["project_horizon_years"] = project_horizon_years
        if discount_rate is not None:
            payload["discount_rate"] = str(discount_rate)
        if status is not None:
            payload["status"] = status.value
        if bank_code is not None:
            payload["bank_code"] = bank_code
        if bank_rate_label is not None:
            payload["bank_rate_label"] = bank_rate_label
        if bank_rate_source_url is not None:
            payload["bank_rate_source_url"] = bank_rate_source_url
        payload.update(
            _extended_payload(
                rep_full_name=rep_full_name,
                rep_email=rep_email,
                rep_id_number=rep_id_number,
                rep_phone=rep_phone,
                rep_role=rep_role,
                company_province=company_province,
                company_municipality=company_municipality,
                company_address=company_address,
                company_activity=company_activity,
                company_phone=company_phone,
                company_email=company_email,
                company_website=company_website,
                company_latitude=company_latitude,
                company_longitude=company_longitude,
                geocode_verified=geocode_verified,
                geocode_source=geocode_source,
                financing_type=financing_type,
                loan_term_months=loan_term_months,
                bank_branch=bank_branch,
            )
        )

        if not payload:
            project = self.find_by_id(project_id)
            if project is None:
                raise EntityNotFoundError("Projeto", str(project_id))
            return project

        response = (
            self._client.table(self.TABLE)
            .update(payload)
            .eq("id", str(project_id))
            .is_("deleted_at", "null")
            .execute()
        )
        rows = get_rows(response)
        if not rows:
            raise EntityNotFoundError("Projeto", str(project_id))
        return map_project_row(rows[0])

    def soft_delete(self, project_id: UUID) -> Project:
        deleted_at = datetime.now(timezone.utc).isoformat()
        response = (
            self._client.table(self.TABLE)
            .update({"deleted_at": deleted_at})
            .eq("id", str(project_id))
            .is_("deleted_at", "null")
            .execute()
        )
        rows = get_rows(response)
        if not rows:
            raise EntityNotFoundError("Projeto", str(project_id))
        return map_project_row(rows[0])

    def is_shared_with_user(self, project_id: UUID, user_id: UUID) -> bool:
        response = (
            self._client.table(self.SHARES_TABLE)
            .select("id")
            .eq("project_id", str(project_id))
            .eq("user_id", str(user_id))
            .limit(1)
            .execute()
        )
        return get_single_row(response) is not None

    def set_has_approved_budget(self, project_id: UUID, value: bool) -> None:
        self._client.table(self.TABLE).update(
            {"has_approved_budget": value}
        ).eq("id", str(project_id)).execute()

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
        payload = {
            "mission": mission,
            "vision": vision,
            "core_values": core_values,
            "swot_analysis": swot_analysis,
            "risk_register": risk_register,
            "aipex_incentives": aipex_incentives,
            "strategic_generated_at": strategic_generated_at.isoformat(),
        }
        response = (
            self._client.table(self.TABLE)
            .update(payload)
            .eq("id", str(project_id))
            .is_("deleted_at", "null")
            .execute()
        )
        rows = get_rows(response)
        if not rows:
            raise EntityNotFoundError("Projeto", str(project_id))
        return map_project_row(rows[0])
