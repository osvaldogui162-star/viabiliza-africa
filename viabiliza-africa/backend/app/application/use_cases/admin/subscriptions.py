from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.application.services.admin_access_policy import AdminAccessPolicy
from app.application.use_cases.admin.mappers import to_plan_output, to_subscription_output
from app.domain.enums.access_action import AccessAction
from app.domain.enums.subscription_status import SubscriptionStatus
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, ValidationError
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.admin_config_repository import ISubscriptionRepository
from app.domain.repositories.user_repository import IUserRepository


class ListSubscriptionPlansUseCase:
    """UC39 — Listar planos."""

    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: ISubscriptionRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository

    def execute(self, *, actor_id: UUID, active_only: bool = False) -> dict:
        self._policy.require_admin(actor_id)
        items = self._repo.find_all_plans(active_only=active_only)
        return {"items": [to_plan_output(p) for p in items], "total": len(items)}


class CreateSubscriptionPlanUseCase:
    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: ISubscriptionRepository,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository
        self._logs = access_log_repository

    def execute(self, *, actor_id: UUID, **kwargs) -> dict:
        self._policy.require_admin(actor_id)
        if self._repo.find_plan_by_code(kwargs["code"]):
            raise ValidationError(f"Plano «{kwargs['code']}» já existe")

        plan = self._repo.create_plan(
            code=kwargs["code"],
            name=kwargs["name"],
            description=kwargs.get("description"),
            price_monthly=Decimal(str(kwargs.get("price_monthly", 0))),
            price_yearly=Decimal(str(kwargs["price_yearly"])) if kwargs.get("price_yearly") is not None else None,
            currency=kwargs.get("currency", "USD"),
            max_projects=kwargs.get("max_projects"),
            max_users=kwargs.get("max_users"),
            max_monte_carlo_iterations=kwargs.get("max_monte_carlo_iterations", 1000),
            features=kwargs.get("features") or {},
            is_active=kwargs.get("is_active", True),
            display_order=kwargs.get("display_order", 0),
        )
        self._logs.create(
            user_id=actor_id,
            action=AccessAction.PLAN_UPDATED,
            metadata={"type": "plan", "code": plan.code, "action": "created"},
        )
        return to_plan_output(plan)


class UpdateSubscriptionPlanUseCase:
    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: ISubscriptionRepository,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository
        self._logs = access_log_repository

    def execute(self, *, actor_id: UUID, plan_id: UUID, **kwargs) -> dict:
        self._policy.require_admin(actor_id)
        if self._repo.find_plan_by_id(plan_id) is None:
            raise EntityNotFoundError("Plano", str(plan_id))

        if "price_monthly" in kwargs and kwargs["price_monthly"] is not None:
            kwargs["price_monthly"] = Decimal(str(kwargs["price_monthly"]))
        if "price_yearly" in kwargs and kwargs["price_yearly"] is not None:
            kwargs["price_yearly"] = Decimal(str(kwargs["price_yearly"]))

        plan = self._repo.update_plan(plan_id, **{k: v for k, v in kwargs.items() if v is not None})
        self._logs.create(
            user_id=actor_id,
            action=AccessAction.PLAN_UPDATED,
            metadata={"type": "plan", "id": str(plan_id), "action": "updated"},
        )
        return to_plan_output(plan)


class DeleteSubscriptionPlanUseCase:
    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: ISubscriptionRepository,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository
        self._logs = access_log_repository

    def execute(self, *, actor_id: UUID, plan_id: UUID) -> dict:
        self._policy.require_admin(actor_id)
        existing = self._repo.find_plan_by_id(plan_id)
        if existing is None:
            raise EntityNotFoundError("Plano", str(plan_id))
        if existing.code == "free":
            raise ValidationError("O plano gratuito não pode ser removido")

        self._repo.delete_plan(plan_id)
        self._logs.create(
            user_id=actor_id,
            action=AccessAction.PLAN_UPDATED,
            metadata={"type": "plan", "code": existing.code, "action": "deleted"},
        )
        return {"message": "Plano removido", "code": existing.code}


class ListUserSubscriptionsUseCase:
    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: ISubscriptionRepository,
        user_repository: IUserRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository
        self._users = user_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        user_id: UUID | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        self._policy.require_admin(actor_id)
        subs = self._repo.find_subscriptions(
            user_id=user_id, status=status, limit=limit, offset=offset
        )
        total = self._repo.count_subscriptions(user_id=user_id, status=status)
        items = []
        for sub in subs:
            plan = self._repo.find_plan_by_id(sub.plan_id)
            user = self._users.find_by_id(sub.user_id)
            items.append(to_subscription_output(sub, plan, user=user))
        return {"items": items, "total": total, "limit": limit, "offset": offset}


class AssignUserSubscriptionUseCase:
    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: ISubscriptionRepository,
        user_repository: IUserRepository,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository
        self._users = user_repository
        self._logs = access_log_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        user_id: UUID,
        plan_id: UUID,
        status: str = "active",
        ends_at: datetime | None = None,
    ) -> dict:
        self._policy.require_admin(actor_id)
        if self._users.find_by_id(user_id) is None:
            raise EntityNotFoundError("Utilizador", str(user_id))
        if self._repo.find_plan_by_id(plan_id) is None:
            raise EntityNotFoundError("Plano", str(plan_id))

        sub = self._repo.assign_subscription(
            user_id=user_id,
            plan_id=plan_id,
            status=SubscriptionStatus(status),
            ends_at=ends_at,
            created_by=actor_id,
        )
        plan = self._repo.find_plan_by_id(plan_id)
        self._logs.create(
            user_id=actor_id,
            action=AccessAction.SUBSCRIPTION_ASSIGNED,
            metadata={"target_user_id": str(user_id), "plan_id": str(plan_id)},
        )
        return to_subscription_output(sub, plan)


class UpdateUserSubscriptionStatusUseCase:
    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: ISubscriptionRepository,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository
        self._logs = access_log_repository

    def execute(self, *, actor_id: UUID, subscription_id: UUID, status: str) -> dict:
        self._policy.require_admin(actor_id)
        sub = self._repo.update_subscription_status(
            subscription_id, SubscriptionStatus(status)
        )
        plan = self._repo.find_plan_by_id(sub.plan_id)
        self._logs.create(
            user_id=actor_id,
            action=AccessAction.SUBSCRIPTION_ASSIGNED,
            metadata={"subscription_id": str(subscription_id), "status": status},
        )
        return to_subscription_output(sub, plan)
