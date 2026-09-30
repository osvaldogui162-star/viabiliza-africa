from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.enums.budget_template_type import BudgetTemplateType
from app.domain.enums.integration_key import IntegrationKey
from app.domain.enums.subscription_status import SubscriptionStatus


@dataclass
class ScrapingSourceConfig:
    id: UUID
    code: str
    name: str
    base_url: str
    is_active: bool
    description: str | None
    country: str
    config: dict
    created_at: datetime
    updated_at: datetime
    updated_by: UUID | None = None


@dataclass
class IntegrationSetting:
    id: UUID
    integration_key: IntegrationKey
    settings: dict
    is_active: bool
    updated_by: UUID | None
    updated_at: datetime
    created_at: datetime


@dataclass
class BudgetTemplate:
    id: UUID
    code: str
    name: str
    template_type: BudgetTemplateType
    header_html: str | None
    footer_html: str | None
    logo_url: str | None
    primary_color: str
    fields: dict
    is_default: bool
    is_active: bool
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime


@dataclass
class SubscriptionPlan:
    id: UUID
    code: str
    name: str
    description: str | None
    price_monthly: Decimal
    price_yearly: Decimal | None
    currency: str
    max_projects: int | None
    max_users: int | None
    max_monte_carlo_iterations: int
    features: dict
    is_active: bool
    display_order: int
    created_at: datetime
    updated_at: datetime


@dataclass
class UserSubscription:
    id: UUID
    user_id: UUID
    plan_id: UUID
    status: SubscriptionStatus
    starts_at: datetime
    ends_at: datetime | None
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime
