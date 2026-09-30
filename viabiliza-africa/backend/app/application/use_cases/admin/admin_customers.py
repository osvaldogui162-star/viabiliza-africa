from datetime import datetime, timezone
from uuid import UUID

from app.application.services.admin_access_policy import AdminAccessPolicy
from app.application.use_cases.admin.mappers import to_subscription_output
from app.domain.repositories.admin_config_repository import ISubscriptionRepository
from app.domain.repositories.payment_repository import ISubscriptionPaymentRepository
from app.domain.repositories.user_repository import IUserRepository


class ListAdminCustomersUseCase:
    """Painel de clientes — utilizador + subscrição + pagamento + projectos."""

    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        user_repository: IUserRepository,
        subscription_repository: ISubscriptionRepository,
        payment_repository: ISubscriptionPaymentRepository,
    ) -> None:
        self._policy = admin_policy
        self._users = user_repository
        self._subs = subscription_repository
        self._payments = payment_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        self._policy.require_admin(actor_id)
        users = self._users.find_all(limit=limit, offset=offset)
        total = self._users.count()
        items = []
        for user in users:
            active = self._subs.find_active_subscription(user.id)
            history = self._subs.find_subscriptions(user_id=user.id, limit=1)
            sub = active or (history[0] if history else None)
            plan = self._subs.find_plan_by_id(sub.plan_id) if sub else None
            latest_payment = self._payments.find_latest_for_user(user.id)
            projects_count = self._subs.count_user_projects(user.id)

            subscription_data = None
            if sub:
                subscription_data = to_subscription_output(sub, plan)
                subscription_data["user_email"] = user.email
                subscription_data["user_name"] = user.full_name

            items.append(
                {
                    "user": {
                        "id": str(user.id),
                        "email": user.email,
                        "full_name": user.full_name,
                        "role": user.role.value,
                        "is_active": user.is_active,
                        "preferred_currency": getattr(user, "preferred_currency", None),
                        "created_at": user.created_at.isoformat(),
                    },
                    "subscription": subscription_data,
                    "latest_payment": latest_payment,
                    "projects_count": projects_count,
                    "billing_status": self._billing_status(sub, latest_payment),
                }
            )

        return {"items": items, "total": total, "limit": limit, "offset": offset}

    @staticmethod
    def _billing_status(sub, latest_payment) -> str:
        if latest_payment and latest_payment.get("status") == "pending":
            return "payment_pending"
        if sub is None:
            return "no_subscription"
        status = sub.status.value
        if status == "active" and sub.ends_at:
            days = (sub.ends_at - datetime.now(timezone.utc)).days
            if days <= 30:
                return "active_expiring"
        return status
