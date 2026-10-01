"""Elegibilidade ERP/facturação — plano pago activo + pagamento verificado (AppyPay)."""

from __future__ import annotations

from uuid import UUID

from app.application.services.subscription_service import SubscriptionService
from app.domain.entities.user import User
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.domain_exceptions import ValidationError
from app.domain.repositories.admin_config_repository import ISubscriptionRepository
from app.domain.repositories.erp_billing_repository import IAccountErpBillingRepository


PAID_PLAN_CODES = frozenset(
    {"starter", "business", "enterprise", "academia_institutional", "government"}
)


class ErpBillingEntitlementService:
    def __init__(
        self,
        subscription_repository: ISubscriptionRepository,
        subscription_service: SubscriptionService,
        erp_billing_repository: IAccountErpBillingRepository,
    ) -> None:
        self._subs_repo = subscription_repository
        self._subs = subscription_service
        self._erp = erp_billing_repository

    def ensure_can_use_erp_billing(self, user: User) -> None:
        if user.role == UserRole.ADMIN:
            return
        plan = self._subs.get_user_plan(user.id)
        features = plan.features or {}
        if not features.get("erp_billing_integration"):
            raise ValidationError(
                "Integração ERP/facturação disponível a partir do plano Starter (pago). "
                "Actualize em /planos."
            )
        if plan.code == "free":
            raise ValidationError(
                "Plano gratuito não inclui ERP de facturação. Subscreva um plano pago em /planos."
            )
        subscription = self._subs_repo.find_active_subscription(user.id)
        if subscription is None and plan.code in PAID_PLAN_CODES:
            raise ValidationError(
                "Assinatura activa em falta. Conclua o pagamento do plano para activar o ERP."
            )
        if plan.code in ("starter", "business") and not self._erp.user_has_paid_subscription_payment(
            user.id
        ):
            raise ValidationError(
                "ERP de facturação requer pelo menos um pagamento de assinatura confirmado (AppyPay)."
            )

    def can_auto_fiscal_on_payment(self, user_id: UUID) -> bool:
        plan = self._subs.get_user_plan(user_id)
        return bool((plan.features or {}).get("erp_auto_fiscal_invoice"))
