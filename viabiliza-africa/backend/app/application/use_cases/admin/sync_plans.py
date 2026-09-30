from uuid import UUID

from app.application.services.admin_access_policy import AdminAccessPolicy
from app.application.use_cases.admin.mappers import to_plan_output
from app.application.use_cases.subscriptions.public_plans import to_public_plan_output
from app.domain.catalog.subscription_plan_catalog import (
    DEPRECATED_PLAN_CODES,
    SUBSCRIPTION_PLAN_CATALOG,
)
from app.domain.enums.access_action import AccessAction
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.admin_config_repository import ISubscriptionRepository


class SyncSubscriptionPlansUseCase:
    """Sincroniza planos com o catálogo comercial (/planos)."""

    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: ISubscriptionRepository,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository
        self._logs = access_log_repository

    def execute(self, *, actor_id: UUID) -> dict:
        self._policy.require_admin(actor_id)
        created = updated = 0
        items = []
        for entry in SUBSCRIPTION_PLAN_CATALOG:
            existing = self._repo.find_plan_by_code(entry["code"])
            if existing:
                plan = self._repo.update_plan(
                    existing.id,
                    name=entry["name"],
                    description=entry["description"],
                    price_monthly=entry["price_monthly"],
                    price_yearly=entry["price_yearly"],
                    currency=entry["currency"],
                    max_projects=entry["max_projects"],
                    max_users=entry["max_users"],
                    max_monte_carlo_iterations=entry["max_monte_carlo_iterations"],
                    features=entry["features"],
                    is_active=True,
                    display_order=entry["display_order"],
                )
                updated += 1
            else:
                plan = self._repo.create_plan(
                    code=entry["code"],
                    name=entry["name"],
                    description=entry["description"],
                    price_monthly=entry["price_monthly"],
                    price_yearly=entry["price_yearly"],
                    currency=entry["currency"],
                    max_projects=entry["max_projects"],
                    max_users=entry["max_users"],
                    max_monte_carlo_iterations=entry["max_monte_carlo_iterations"],
                    features=entry["features"],
                    is_active=True,
                    display_order=entry["display_order"],
                )
                created += 1
            items.append(to_public_plan_output(plan))

        for legacy_code in DEPRECATED_PLAN_CODES:
            legacy = self._repo.find_plan_by_code(legacy_code)
            if legacy and legacy.is_active:
                self._repo.update_plan(legacy.id, is_active=False)
                updated += 1

        self._logs.create(
            user_id=actor_id,
            action=AccessAction.PLAN_UPDATED,
            metadata={"action": "sync_catalog", "created": created, "updated": updated},
        )
        return {"created": created, "updated": updated, "items": items, "total": len(items)}
