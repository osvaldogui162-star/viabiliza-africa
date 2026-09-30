from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

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


class IScrapingSourceAdminRepository(ABC):
    @abstractmethod
    def find_all(self) -> list[ScrapingSourceConfig]:
        ...

    @abstractmethod
    def find_by_id(self, source_id: UUID) -> ScrapingSourceConfig | None:
        ...

    @abstractmethod
    def find_by_code(self, code: str) -> ScrapingSourceConfig | None:
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def delete(self, source_id: UUID) -> None:
        ...


class IIntegrationSettingsRepository(ABC):
    @abstractmethod
    def find_all(self) -> list[IntegrationSetting]:
        ...

    @abstractmethod
    def find_by_key(self, key: IntegrationKey) -> IntegrationSetting | None:
        ...

    @abstractmethod
    def upsert(
        self,
        key: IntegrationKey,
        *,
        settings: dict,
        is_active: bool,
        updated_by: UUID,
    ) -> IntegrationSetting:
        ...


class IBudgetTemplateRepository(ABC):
    @abstractmethod
    def find_all(self, *, active_only: bool = False) -> list[BudgetTemplate]:
        ...

    @abstractmethod
    def find_by_id(self, template_id: UUID) -> BudgetTemplate | None:
        ...

    @abstractmethod
    def find_default(self, template_type: BudgetTemplateType | None = None) -> BudgetTemplate | None:
        ...

    @abstractmethod
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
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def set_default(self, template_id: UUID) -> BudgetTemplate:
        ...

    @abstractmethod
    def delete(self, template_id: UUID) -> None:
        ...


class ISubscriptionRepository(ABC):
    @abstractmethod
    def find_all_plans(self, *, active_only: bool = False) -> list[SubscriptionPlan]:
        ...

    @abstractmethod
    def find_plan_by_id(self, plan_id: UUID) -> SubscriptionPlan | None:
        ...

    @abstractmethod
    def find_plan_by_code(self, code: str) -> SubscriptionPlan | None:
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def update_plan(self, plan_id: UUID, **kwargs) -> SubscriptionPlan:
        ...

    @abstractmethod
    def delete_plan(self, plan_id: UUID) -> None:
        ...

    @abstractmethod
    def find_active_subscription(self, user_id: UUID) -> UserSubscription | None:
        ...

    @abstractmethod
    def find_subscriptions(
        self,
        *,
        user_id: UUID | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[UserSubscription]:
        ...

    @abstractmethod
    def count_subscriptions(
        self,
        *,
        user_id: UUID | None = None,
        status: str | None = None,
        plan_id: UUID | None = None,
    ) -> int:
        ...

    @abstractmethod
    def assign_subscription(
        self,
        *,
        user_id: UUID,
        plan_id: UUID,
        status: SubscriptionStatus,
        ends_at,
        created_by: UUID,
    ) -> UserSubscription:
        ...

    @abstractmethod
    def update_subscription_status(
        self, subscription_id: UUID, status: SubscriptionStatus
    ) -> UserSubscription:
        ...

    @abstractmethod
    def count_user_projects(self, user_id: UUID) -> int:
        ...

    @abstractmethod
    def count_user_scraping_items_this_month(self, user_id: UUID) -> int:
        ...

    @abstractmethod
    def count_owner_collaborators(self, owner_id: UUID) -> int:
        ...

    @abstractmethod
    def find_owner_collaborator_ids(self, owner_id: UUID) -> set[UUID]:
        ...
