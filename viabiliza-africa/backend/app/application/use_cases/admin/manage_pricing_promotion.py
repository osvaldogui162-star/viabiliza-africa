from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.application.services.admin_access_policy import AdminAccessPolicy
from app.application.services.commercial_pricing_service import CommercialPricingService
from app.domain.enums.access_action import AccessAction
from app.domain.exceptions.domain_exceptions import ValidationError
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.platform_settings_repository import IPlatformSettingsRepository


class ManagePricingPromotionUseCase:
    """Activar/desactivar campanha comercial (−20% sobre preço de referência)."""

    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        platform_settings: IPlatformSettingsRepository,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._policy = admin_policy
        self._settings = platform_settings
        self._logs = access_log_repository
        self._pricing = CommercialPricingService(platform_settings)

    def get_status(self, *, actor_id: UUID) -> dict:
        self._policy.require_admin(actor_id)
        return self._pricing.get_promotion_state()

    def get_overview(self, *, actor_id: UUID) -> dict:
        self._policy.require_admin(actor_id)
        return self._pricing.build_admin_overview()

    def activate(
        self,
        *,
        actor_id: UUID,
        duration_months: int = 3,
    ) -> dict:
        self._policy.require_admin(actor_id)
        if duration_months not in (3, 4, 5, 6):
            raise ValidationError("A campanha deve durar entre 3 e 6 meses.")

        now = datetime.now(timezone.utc)
        ends = now + timedelta(days=30 * duration_months)
        payload = {
            "active": True,
            "started_at": now.isoformat(),
            "ends_at": ends.isoformat(),
            "duration_months": duration_months,
            "discount_pct": 20,
            "activated_by": str(actor_id),
        }
        try:
            self._settings.set_pricing_promotion(payload)
        except Exception as exc:
            raise ValidationError(
                "Não foi possível guardar a campanha. Execute a migration "
                "025_commercial_pricing_cycles.sql no Supabase (tabela platform_settings)."
            ) from exc
        self._logs.create(
            user_id=actor_id,
            action=AccessAction.PLAN_UPDATED,
            metadata={"action": "pricing_promotion_activate", **payload},
        )
        return self._pricing.build_admin_overview()

    def deactivate(self, *, actor_id: UUID) -> dict:
        self._policy.require_admin(actor_id)
        payload = {"active": False, "deactivated_at": datetime.now(timezone.utc).isoformat()}
        try:
            self._settings.set_pricing_promotion(payload)
        except Exception as exc:
            raise ValidationError(
                "Não foi possível actualizar a campanha. Verifique a migration "
                "025_commercial_pricing_cycles.sql no Supabase."
            ) from exc
        self._logs.create(
            user_id=actor_id,
            action=AccessAction.PLAN_UPDATED,
            metadata={"action": "pricing_promotion_deactivate"},
        )
        return self._pricing.build_admin_overview()
