from datetime import datetime, timezone

from app.application.services.integration_config_service import mask_settings
from app.domain.entities.admin_config import (
    BudgetTemplate,
    IntegrationSetting,
    ScrapingSourceConfig,
    SubscriptionPlan,
    UserSubscription,
)


def to_scraping_source_output(source: ScrapingSourceConfig) -> dict:
    return {
        "id": str(source.id),
        "code": source.code,
        "name": source.name,
        "base_url": source.base_url,
        "description": source.description,
        "country": source.country,
        "config": source.config,
        "is_active": source.is_active,
        "updated_at": source.updated_at.isoformat(),
    }


def to_integration_output(setting: IntegrationSetting, *, masked: bool = True) -> dict:
    return {
        "integration_key": setting.integration_key.value,
        "settings": mask_settings(setting.settings) if masked else setting.settings,
        "is_active": setting.is_active,
        "updated_at": setting.updated_at.isoformat(),
    }


def to_template_output(template: BudgetTemplate) -> dict:
    return {
        "id": str(template.id),
        "code": template.code,
        "name": template.name,
        "template_type": template.template_type.value,
        "header_html": template.header_html,
        "footer_html": template.footer_html,
        "logo_url": template.logo_url,
        "primary_color": template.primary_color,
        "fields": template.fields,
        "is_default": template.is_default,
        "is_active": template.is_active,
        "updated_at": template.updated_at.isoformat(),
    }


def to_plan_output(plan: SubscriptionPlan) -> dict:
    return {
        "id": str(plan.id),
        "code": plan.code,
        "name": plan.name,
        "description": plan.description,
        "price_monthly": str(plan.price_monthly),
        "price_yearly": str(plan.price_yearly) if plan.price_yearly is not None else None,
        "currency": plan.currency,
        "max_projects": plan.max_projects,
        "max_users": plan.max_users,
        "max_monte_carlo_iterations": plan.max_monte_carlo_iterations,
        "features": plan.features,
        "is_active": plan.is_active,
        "display_order": plan.display_order,
    }


def to_subscription_output(sub: UserSubscription, plan: SubscriptionPlan | None = None, *, user=None) -> dict:
    now = datetime.now(timezone.utc)
    data = {
        "id": str(sub.id),
        "user_id": str(sub.user_id),
        "plan_id": str(sub.plan_id),
        "status": sub.status.value,
        "starts_at": sub.starts_at.isoformat(),
        "ends_at": sub.ends_at.isoformat() if sub.ends_at else None,
        "created_at": sub.created_at.isoformat(),
        "days_remaining": None,
        "is_expiring_soon": False,
    }
    if sub.ends_at and sub.status.value in ("active", "trial"):
        remaining = (sub.ends_at - now).days
        data["days_remaining"] = max(remaining, 0)
        data["is_expiring_soon"] = 0 <= remaining <= 30
    if plan:
        data["plan"] = to_plan_output(plan)
    if user:
        data["user_email"] = user.email
        data["user_name"] = user.full_name
    return data


def to_payment_admin_output(payment: dict, *, user_email: str | None = None, user_name: str | None = None) -> dict:
    return {
        **payment,
        "user_email": user_email,
        "user_name": user_name,
    }
