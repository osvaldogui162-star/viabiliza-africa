from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from app.application.services.admin_access_policy import AdminAccessPolicy
from app.application.use_cases.admin.mappers import to_payment_admin_output, to_subscription_output
from app.domain.repositories.admin_config_repository import ISubscriptionRepository
from app.domain.repositories.payment_repository import ISubscriptionPaymentRepository
from app.domain.repositories.user_repository import IUserRepository


class GetBillingOverviewUseCase:
    """Resumo financeiro e operacional para o painel admin."""

    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        subscription_repository: ISubscriptionRepository,
        payment_repository: ISubscriptionPaymentRepository,
        user_repository: IUserRepository,
    ) -> None:
        self._policy = admin_policy
        self._subs = subscription_repository
        self._payments = payment_repository
        self._users = user_repository

    def execute(self, *, actor_id: UUID) -> dict:
        self._policy.require_admin(actor_id)
        now = datetime.now(timezone.utc)
        in_7 = now + timedelta(days=7)
        in_30 = now + timedelta(days=30)

        subs = self._subs.find_subscriptions(limit=500, offset=0)
        active = trial = expired = cancelled = expiring_7 = expiring_30 = 0
        for sub in subs:
            if sub.status.value == "active":
                active += 1
                if sub.ends_at:
                    if sub.ends_at <= in_7:
                        expiring_7 += 1
                    elif sub.ends_at <= in_30:
                        expiring_30 += 1
            elif sub.status.value == "trial":
                trial += 1
            elif sub.status.value == "expired":
                expired += 1
            elif sub.status.value == "cancelled":
                cancelled += 1

        payment_stats = self._payments.get_admin_stats()

        plans = self._subs.find_all_plans(active_only=False)
        subscribers_by_plan = []
        for plan in plans:
            active_count = self._subs.count_subscriptions(plan_id=plan.id, status="active")
            total_count = self._subs.count_subscriptions(plan_id=plan.id)
            features = plan.features or {}
            subscribers_by_plan.append(
                {
                    "plan_id": str(plan.id),
                    "plan_code": plan.code,
                    "plan_name": plan.name,
                    "emoji": features.get("emoji"),
                    "active_subscribers": active_count,
                    "total_subscriptions": total_count,
                    "is_active": plan.is_active,
                }
            )

        recent_raw, _ = self._payments.find_all(limit=8, offset=0)
        recent_payments = []
        user_cache: dict[str, object] = {}
        for payment in recent_raw:
            uid = payment["user_id"]
            if uid not in user_cache:
                user_cache[uid] = self._users.find_by_id(UUID(uid))
            user = user_cache[uid]
            recent_payments.append(
                to_payment_admin_output(
                    payment,
                    user_email=user.email if user else None,
                    user_name=user.full_name if user else None,
                )
            )

        return {
            "users_total": self._users.count(),
            "subscriptions": {
                "active": active,
                "trial": trial,
                "expired": expired,
                "cancelled": cancelled,
                "expiring_7_days": expiring_7,
                "expiring_30_days": expiring_30,
                "total": len(subs),
            },
            "payments": payment_stats,
            "subscribers_by_plan": subscribers_by_plan,
            "recent_payments": recent_payments,
        }


class ListAdminPaymentsUseCase:
    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        payment_repository: ISubscriptionPaymentRepository,
        user_repository: IUserRepository,
    ) -> None:
        self._policy = admin_policy
        self._payments = payment_repository
        self._users = user_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        status: str | None = None,
        user_id: UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        self._policy.require_admin(actor_id)
        items, total = self._payments.find_all(
            status=status, user_id=user_id, limit=limit, offset=offset
        )
        user_cache: dict[str, object] = {}
        output = []
        for payment in items:
            uid = payment["user_id"]
            if uid not in user_cache:
                user_cache[uid] = self._users.find_by_id(UUID(uid))
            user = user_cache[uid]
            output.append(
                to_payment_admin_output(
                    payment,
                    user_email=user.email if user else None,
                    user_name=user.full_name if user else None,
                )
            )
        return {"items": output, "total": total, "limit": limit, "offset": offset}
