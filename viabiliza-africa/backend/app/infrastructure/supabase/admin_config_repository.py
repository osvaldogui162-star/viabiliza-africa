from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from supabase import Client

from app.domain.entities.admin_config import (
    BudgetTemplate,
    IntegrationSetting,
    ScrapingSourceConfig,
    SubscriptionPlan,
    UserSubscription,
)
from app.domain.enums.budget_template_type import BudgetTemplateType
from app.domain.enums.integration_key import IntegrationKey
from app.domain.enums.subscription_status import SubscriptionStatus
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from app.domain.repositories.admin_config_repository import (
    IBudgetTemplateRepository,
    IIntegrationSettingsRepository,
    IScrapingSourceAdminRepository,
    ISubscriptionRepository,
)
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _map_scraping_source(row: dict) -> ScrapingSourceConfig:
    return ScrapingSourceConfig(
        id=UUID(row["id"]),
        code=row["code"],
        name=row["name"],
        base_url=row["base_url"],
        is_active=row["is_active"],
        description=row.get("description"),
        country=row.get("country") or "AO",
        config=row.get("config") or {},
        created_at=_parse_dt(row["created_at"]),
        updated_at=_parse_dt(row.get("updated_at") or row["created_at"]),
        updated_by=UUID(row["updated_by"]) if row.get("updated_by") else None,
    )


def _map_integration(row: dict) -> IntegrationSetting:
    return IntegrationSetting(
        id=UUID(row["id"]),
        integration_key=IntegrationKey(row["integration_key"]),
        settings=row.get("settings") or {},
        is_active=row["is_active"],
        updated_by=UUID(row["updated_by"]) if row.get("updated_by") else None,
        updated_at=_parse_dt(row["updated_at"]),
        created_at=_parse_dt(row["created_at"]),
    )


def _map_template(row: dict) -> BudgetTemplate:
    return BudgetTemplate(
        id=UUID(row["id"]),
        code=row["code"],
        name=row["name"],
        template_type=BudgetTemplateType(row["template_type"]),
        header_html=row.get("header_html"),
        footer_html=row.get("footer_html"),
        logo_url=row.get("logo_url"),
        primary_color=row.get("primary_color") or "#1a5276",
        fields=row.get("fields") or {},
        is_default=row["is_default"],
        is_active=row["is_active"],
        created_by=UUID(row["created_by"]) if row.get("created_by") else None,
        created_at=_parse_dt(row["created_at"]),
        updated_at=_parse_dt(row.get("updated_at") or row["created_at"]),
    )


def _map_plan(row: dict) -> SubscriptionPlan:
    return SubscriptionPlan(
        id=UUID(row["id"]),
        code=row["code"],
        name=row["name"],
        description=row.get("description"),
        price_monthly=Decimal(str(row["price_monthly"])),
        price_yearly=Decimal(str(row["price_yearly"])) if row.get("price_yearly") is not None else None,
        currency=row["currency"],
        max_projects=row.get("max_projects"),
        max_users=row.get("max_users"),
        max_monte_carlo_iterations=row["max_monte_carlo_iterations"],
        features=row.get("features") or {},
        is_active=row["is_active"],
        display_order=row.get("display_order", 0),
        created_at=_parse_dt(row["created_at"]),
        updated_at=_parse_dt(row.get("updated_at") or row["created_at"]),
    )


def _map_subscription(row: dict) -> UserSubscription:
    return UserSubscription(
        id=UUID(row["id"]),
        user_id=UUID(row["user_id"]),
        plan_id=UUID(row["plan_id"]),
        status=SubscriptionStatus(row["status"]),
        starts_at=_parse_dt(row["starts_at"]),
        ends_at=_parse_dt(row["ends_at"]) if row.get("ends_at") else None,
        created_by=UUID(row["created_by"]) if row.get("created_by") else None,
        created_at=_parse_dt(row["created_at"]),
        updated_at=_parse_dt(row.get("updated_at") or row["created_at"]),
    )


class SupabaseScrapingSourceAdminRepository(IScrapingSourceAdminRepository):
    TABLE = "scraping_sources"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_all(self) -> list[ScrapingSourceConfig]:
        response = self._client.table(self.TABLE).select("*").order("name").execute()
        return [_map_scraping_source(r) for r in get_rows(response)]

    def find_by_id(self, source_id: UUID) -> ScrapingSourceConfig | None:
        response = (
            self._client.table(self.TABLE).select("*").eq("id", str(source_id)).limit(1).execute()
        )
        row = get_single_row(response)
        return _map_scraping_source(row) if row else None

    def find_by_code(self, code: str) -> ScrapingSourceConfig | None:
        response = (
            self._client.table(self.TABLE).select("*").eq("code", code).limit(1).execute()
        )
        row = get_single_row(response)
        return _map_scraping_source(row) if row else None

    def create(
        self,
        *,
        code: str,
        name: str,
        base_url: str,
        description: str | None,
        country: str,
        config: dict,
        is_active: bool,
        updated_by: UUID,
    ) -> ScrapingSourceConfig:
        payload = {
            "code": code.strip().lower(),
            "name": name.strip(),
            "base_url": base_url.strip(),
            "description": description,
            "country": country,
            "config": config,
            "is_active": is_active,
            "updated_by": str(updated_by),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        if not row:
            raise RuntimeError("Falha ao criar fonte de scraping")
        return _map_scraping_source(row)

    def update(
        self,
        source_id: UUID,
        *,
        name: str | None = None,
        base_url: str | None = None,
        description: str | None = None,
        country: str | None = None,
        config: dict | None = None,
        is_active: bool | None = None,
        updated_by: UUID | None = None,
    ) -> ScrapingSourceConfig:
        payload: dict = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if name is not None:
            payload["name"] = name.strip()
        if base_url is not None:
            payload["base_url"] = base_url.strip()
        if description is not None:
            payload["description"] = description
        if country is not None:
            payload["country"] = country
        if config is not None:
            payload["config"] = config
        if is_active is not None:
            payload["is_active"] = is_active
        if updated_by is not None:
            payload["updated_by"] = str(updated_by)

        response = (
            self._client.table(self.TABLE).update(payload).eq("id", str(source_id)).execute()
        )
        row = get_single_row(response)
        if not row:
            raise EntityNotFoundError("Fonte de scraping", str(source_id))
        return _map_scraping_source(row)

    def delete(self, source_id: UUID) -> None:
        self._client.table(self.TABLE).delete().eq("id", str(source_id)).execute()


class SupabaseIntegrationSettingsRepository(IIntegrationSettingsRepository):
    TABLE = "integration_settings"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_all(self) -> list[IntegrationSetting]:
        response = self._client.table(self.TABLE).select("*").order("integration_key").execute()
        return [_map_integration(r) for r in get_rows(response)]

    def find_by_key(self, key: IntegrationKey) -> IntegrationSetting | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("integration_key", key.value)
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return _map_integration(row) if row else None

    def upsert(
        self,
        key: IntegrationKey,
        *,
        settings: dict,
        is_active: bool,
        updated_by: UUID,
    ) -> IntegrationSetting:
        existing = self.find_by_key(key)
        payload = {
            "integration_key": key.value,
            "settings": settings,
            "is_active": is_active,
            "updated_by": str(updated_by),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        if existing:
            response = (
                self._client.table(self.TABLE)
                .update(payload)
                .eq("integration_key", key.value)
                .execute()
            )
        else:
            response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        if not row:
            raise RuntimeError(f"Falha ao guardar integração {key.value}")
        return _map_integration(row)


class SupabaseBudgetTemplateRepository(IBudgetTemplateRepository):
    TABLE = "budget_templates"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_all(self, *, active_only: bool = False) -> list[BudgetTemplate]:
        query = self._client.table(self.TABLE).select("*").order("name")
        if active_only:
            query = query.eq("is_active", True)
        response = query.execute()
        return [_map_template(r) for r in get_rows(response)]

    def find_by_id(self, template_id: UUID) -> BudgetTemplate | None:
        response = (
            self._client.table(self.TABLE).select("*").eq("id", str(template_id)).limit(1).execute()
        )
        row = get_single_row(response)
        return _map_template(row) if row else None

    def find_default(self, template_type: BudgetTemplateType | None = None) -> BudgetTemplate | None:
        query = self._client.table(self.TABLE).select("*").eq("is_default", True).eq("is_active", True)
        response = query.limit(1).execute()
        row = get_single_row(response)
        if not row:
            return None
        template = _map_template(row)
        if template_type and template.template_type not in (template_type, BudgetTemplateType.BOTH):
            return None
        return template

    def create(
        self,
        *,
        code: str,
        name: str,
        template_type: BudgetTemplateType,
        header_html: str | None,
        footer_html: str | None,
        logo_url: str | None,
        primary_color: str,
        fields: dict,
        is_default: bool,
        is_active: bool,
        created_by: UUID,
    ) -> BudgetTemplate:
        if is_default:
            self._client.table(self.TABLE).update({"is_default": False}).eq("is_default", True).execute()

        payload = {
            "code": code.strip().lower(),
            "name": name.strip(),
            "template_type": template_type.value,
            "header_html": header_html,
            "footer_html": footer_html,
            "logo_url": logo_url,
            "primary_color": primary_color,
            "fields": fields,
            "is_default": is_default,
            "is_active": is_active,
            "created_by": str(created_by),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        if not row:
            raise RuntimeError("Falha ao criar template")
        return _map_template(row)

    def update(
        self,
        template_id: UUID,
        *,
        name: str | None = None,
        template_type: BudgetTemplateType | None = None,
        header_html: str | None = None,
        footer_html: str | None = None,
        logo_url: str | None = None,
        primary_color: str | None = None,
        fields: dict | None = None,
        is_active: bool | None = None,
    ) -> BudgetTemplate:
        payload: dict = {"updated_at": datetime.now(timezone.utc).isoformat()}
        if name is not None:
            payload["name"] = name.strip()
        if template_type is not None:
            payload["template_type"] = template_type.value
        if header_html is not None:
            payload["header_html"] = header_html
        if footer_html is not None:
            payload["footer_html"] = footer_html
        if logo_url is not None:
            payload["logo_url"] = logo_url
        if primary_color is not None:
            payload["primary_color"] = primary_color
        if fields is not None:
            payload["fields"] = fields
        if is_active is not None:
            payload["is_active"] = is_active

        response = (
            self._client.table(self.TABLE).update(payload).eq("id", str(template_id)).execute()
        )
        row = get_single_row(response)
        if not row:
            raise EntityNotFoundError("Template de orçamento", str(template_id))
        return _map_template(row)

    def set_default(self, template_id: UUID) -> BudgetTemplate:
        self._client.table(self.TABLE).update({"is_default": False}).eq("is_default", True).execute()
        response = (
            self._client.table(self.TABLE)
            .update({"is_default": True, "updated_at": datetime.now(timezone.utc).isoformat()})
            .eq("id", str(template_id))
            .execute()
        )
        row = get_single_row(response)
        if not row:
            raise EntityNotFoundError("Template de orçamento", str(template_id))
        return _map_template(row)

    def delete(self, template_id: UUID) -> None:
        template = self.find_by_id(template_id)
        if template and template.is_default:
            raise ValueError("Não é possível remover o template predefinido")
        self._client.table(self.TABLE).delete().eq("id", str(template_id)).execute()


class SupabaseSubscriptionRepository(ISubscriptionRepository):
    PLANS = "subscription_plans"
    SUBS = "user_subscriptions"
    PROJECTS = "projects"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_all_plans(self, *, active_only: bool = False) -> list[SubscriptionPlan]:
        query = self._client.table(self.PLANS).select("*").order("display_order")
        if active_only:
            query = query.eq("is_active", True)
        response = query.execute()
        return [_map_plan(r) for r in get_rows(response)]

    def find_plan_by_id(self, plan_id: UUID) -> SubscriptionPlan | None:
        response = (
            self._client.table(self.PLANS).select("*").eq("id", str(plan_id)).limit(1).execute()
        )
        row = get_single_row(response)
        return _map_plan(row) if row else None

    def find_plan_by_code(self, code: str) -> SubscriptionPlan | None:
        response = (
            self._client.table(self.PLANS).select("*").eq("code", code).limit(1).execute()
        )
        row = get_single_row(response)
        return _map_plan(row) if row else None

    def create_plan(
        self,
        *,
        code: str,
        name: str,
        description: str | None,
        price_monthly: Decimal,
        price_yearly: Decimal | None,
        currency: str,
        max_projects: int | None,
        max_users: int | None,
        max_monte_carlo_iterations: int,
        features: dict,
        is_active: bool,
        display_order: int,
    ) -> SubscriptionPlan:
        payload = {
            "code": code.strip().lower(),
            "name": name.strip(),
            "description": description,
            "price_monthly": str(price_monthly),
            "price_yearly": str(price_yearly) if price_yearly is not None else None,
            "currency": currency,
            "max_projects": max_projects,
            "max_users": max_users,
            "max_monte_carlo_iterations": max_monte_carlo_iterations,
            "features": features,
            "is_active": is_active,
            "display_order": display_order,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        response = self._client.table(self.PLANS).insert(payload).execute()
        row = get_single_row(response)
        if not row:
            raise RuntimeError("Falha ao criar plano")
        return _map_plan(row)

    def update_plan(self, plan_id: UUID, **kwargs) -> SubscriptionPlan:
        payload = {k: v for k, v in kwargs.items() if v is not None}
        if "price_monthly" in payload:
            payload["price_monthly"] = str(payload["price_monthly"])
        if "price_yearly" in payload and payload["price_yearly"] is not None:
            payload["price_yearly"] = str(payload["price_yearly"])
        payload["updated_at"] = datetime.now(timezone.utc).isoformat()

        response = (
            self._client.table(self.PLANS).update(payload).eq("id", str(plan_id)).execute()
        )
        row = get_single_row(response)
        if not row:
            raise EntityNotFoundError("Plano", str(plan_id))
        return _map_plan(row)

    def delete_plan(self, plan_id: UUID) -> None:
        self._client.table(self.PLANS).delete().eq("id", str(plan_id)).execute()

    def find_active_subscription(self, user_id: UUID) -> UserSubscription | None:
        response = (
            self._client.table(self.SUBS)
            .select("*")
            .eq("user_id", str(user_id))
            .eq("status", SubscriptionStatus.ACTIVE.value)
            .order("starts_at", desc=True)
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        if not row:
            return None
        sub = _map_subscription(row)
        if sub.ends_at and sub.ends_at < datetime.now(timezone.utc):
            self.update_subscription_status(sub.id, SubscriptionStatus.EXPIRED)
            return None
        return sub

    def find_subscriptions(
        self,
        *,
        user_id: UUID | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[UserSubscription]:
        query = self._client.table(self.SUBS).select("*").order("created_at", desc=True)
        if user_id:
            query = query.eq("user_id", str(user_id))
        if status:
            query = query.eq("status", status)
        response = query.range(offset, offset + limit - 1).execute()
        return [_map_subscription(r) for r in get_rows(response)]

    def count_subscriptions(
        self,
        *,
        user_id: UUID | None = None,
        status: str | None = None,
        plan_id: UUID | None = None,
    ) -> int:
        query = self._client.table(self.SUBS).select("id", count="exact")
        if user_id:
            query = query.eq("user_id", str(user_id))
        if status:
            query = query.eq("status", status)
        if plan_id:
            query = query.eq("plan_id", str(plan_id))
        response = query.execute()
        return response.count or 0

    def assign_subscription(
        self,
        *,
        user_id: UUID,
        plan_id: UUID,
        status: SubscriptionStatus,
        ends_at,
        created_by: UUID,
    ) -> UserSubscription:
        self._client.table(self.SUBS).update(
            {"status": SubscriptionStatus.CANCELLED.value, "updated_at": datetime.now(timezone.utc).isoformat()}
        ).eq("user_id", str(user_id)).eq("status", SubscriptionStatus.ACTIVE.value).execute()

        payload = {
            "user_id": str(user_id),
            "plan_id": str(plan_id),
            "status": status.value,
            "starts_at": datetime.now(timezone.utc).isoformat(),
            "ends_at": ends_at.isoformat() if ends_at else None,
            "created_by": str(created_by),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        response = self._client.table(self.SUBS).insert(payload).execute()
        row = get_single_row(response)
        if not row:
            raise RuntimeError("Falha ao atribuir assinatura")
        return _map_subscription(row)

    def update_subscription_status(
        self, subscription_id: UUID, status: SubscriptionStatus
    ) -> UserSubscription:
        response = (
            self._client.table(self.SUBS)
            .update({"status": status.value, "updated_at": datetime.now(timezone.utc).isoformat()})
            .eq("id", str(subscription_id))
            .execute()
        )
        row = get_single_row(response)
        if not row:
            raise EntityNotFoundError("Assinatura", str(subscription_id))
        return _map_subscription(row)

    def count_user_projects(self, user_id: UUID) -> int:
        response = (
            self._client.table(self.PROJECTS)
            .select("id", count="exact")
            .eq("owner_id", str(user_id))
            .is_("deleted_at", "null")
            .execute()
        )
        return response.count or 0

    def count_user_scraping_items_this_month(self, user_id: UUID) -> int:
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        projects = (
            self._client.table(self.PROJECTS)
            .select("id")
            .eq("owner_id", str(user_id))
            .is_("deleted_at", "null")
            .execute()
        )
        project_ids = [row["id"] for row in get_rows(projects)]
        if not project_ids:
            return 0
        response = (
            self._client.table("scraping_results")
            .select("id", count="exact")
            .in_("project_id", project_ids)
            .gte("scraped_at", month_start.isoformat())
            .execute()
        )
        return response.count or 0

    def count_owner_collaborators(self, owner_id: UUID) -> int:
        return len(self.find_owner_collaborator_ids(owner_id))

    def find_owner_collaborator_ids(self, owner_id: UUID) -> set[UUID]:
        projects = (
            self._client.table(self.PROJECTS)
            .select("id")
            .eq("owner_id", str(owner_id))
            .is_("deleted_at", "null")
            .execute()
        )
        project_ids = [row["id"] for row in get_rows(projects)]
        if not project_ids:
            return set()

        response = (
            self._client.table("project_shares")
            .select("user_id")
            .in_("project_id", project_ids)
            .execute()
        )
        return {UUID(row["user_id"]) for row in get_rows(response)}
