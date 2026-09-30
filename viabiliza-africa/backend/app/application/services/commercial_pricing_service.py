"""Cálculo de preços, campanhas e recomendações comerciais."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from app.domain.catalog.plan_commercial_pricing import (
    BILLING_PERIOD_DAYS,
    PLAN_AOA_PRICING,
    PLAN_RECOMMENDATION,
    PROMOTION_DISCOUNT_PCT,
    PUBLIC_PLAN_CODES,
    BillingPeriod,
    fixed_aoa,
    promotional_aoa,
    reference_aoa,
)

PLAN_DISPLAY_NAMES: dict[str, str] = {
    "starter": "Starter",
    "business": "Business",
    "enterprise": "Enterprise",
    "academia_institutional": "Academia Institucional",
    "government": "Governo",
}

PERIOD_LABELS_PT = {
    "quarterly": "Trimestral",
    "semiannual": "Semestral",
    "yearly": "Anual",
}

IVA_RATE = Decimal("0.25")
VALID_BILLING_PERIODS = frozenset(BILLING_PERIOD_DAYS.keys())


class CommercialPricingService:
    """Preços fixos AOA + campanha opcional (−20% sobre preço de referência)."""

    def __init__(self, platform_settings_repository) -> None:
        self._settings = platform_settings_repository

    def get_promotion_state(self) -> dict:
        raw = self._settings.get_pricing_promotion()
        active = bool(raw.get("active"))
        ends_at = raw.get("ends_at")
        ends_dt = None
        if ends_at:
            try:
                ends_dt = datetime.fromisoformat(str(ends_at).replace("Z", "+00:00"))
                if ends_dt.tzinfo is None:
                    ends_dt = ends_dt.replace(tzinfo=timezone.utc)
                if ends_dt <= datetime.now(timezone.utc):
                    active = False
            except ValueError:
                active = False
        return {
            "active": active,
            "discount_pct": int(raw.get("discount_pct") or PROMOTION_DISCOUNT_PCT),
            "started_at": raw.get("started_at") if active else None,
            "ends_at": ends_at if active else None,
            "duration_months": raw.get("duration_months") if active else None,
            "label_pt": (
                f"Campanha −{PROMOTION_DISCOUNT_PCT}% sobre o preço de referência"
                if active
                else None
            ),
            "label_en": (
                f"Campaign: {PROMOTION_DISCOUNT_PCT}% off reference pricing"
                if active
                else None
            ),
        }

    def build_admin_overview(self) -> dict:
        promotion = self.get_promotion_state()
        matrix: list[dict] = []
        for code in PUBLIC_PLAN_CODES:
            for period in ("quarterly", "semiannual", "yearly"):
                amount = self.build_amount(code, period)
                matrix.append(
                    {
                        "plan_code": code,
                        "plan_name": PLAN_DISPLAY_NAMES.get(code, code),
                        "billing_period": period,
                        "billing_period_label_pt": PERIOD_LABELS_PT[period],
                        "fixed_aoa": amount["price_fixed_aoa"],
                        "reference_aoa": amount["price_reference_aoa"],
                        "promotional_aoa": amount["price_promotional_aoa"],
                        "checkout_subtotal_aoa": int(Decimal(amount["subtotal"])),
                        "checkout_total_aoa": int(Decimal(amount["total"])),
                        "promotion_applied": amount["promotion_applied"],
                    }
                )
        return {
            "promotion": promotion,
            "pricing_rules": {
                "currency": "AOA",
                "vat_rate_pct": 25,
                "discount_basis": "reference_price",
                "description_pt": (
                    "Com campanha activa, o checkout cobra 20% de desconto sobre o preço "
                    "de referência (antigo). Sem campanha, aplica-se o preço fixo do catálogo."
                ),
                "description_en": (
                    "When the campaign is active, checkout charges 20% off the reference "
                    "(legacy) price. Otherwise the fixed catalog price applies."
                ),
            },
            "matrix": matrix,
        }

    def resolve_subtotal_aoa(self, plan_code: str, billing_period: str, *, promo: bool | None = None) -> int:
        code = plan_code.strip().lower()
        period: BillingPeriod = billing_period  # type: ignore[assignment]
        if period not in VALID_BILLING_PERIODS:
            raise ValueError("invalid billing period")
        if code not in PLAN_AOA_PRICING:
            raise ValueError("unknown plan")
        if promo is None:
            promo = self.get_promotion_state()["active"]
        if promo:
            return promotional_aoa(code, period)
        return fixed_aoa(code, period)

    def build_amount(self, plan_code: str, billing_period: str) -> dict:
        promo = self.get_promotion_state()
        code = plan_code.strip().lower()
        period = billing_period
        reference = reference_aoa(code, period)  # type: ignore[arg-type]
        fixed = fixed_aoa(code, period)  # type: ignore[arg-type]
        subtotal_int = self.resolve_subtotal_aoa(code, period, promo=promo["active"])
        subtotal = Decimal(subtotal_int)
        vat = (subtotal * IVA_RATE).quantize(Decimal("0.01"))
        total = subtotal + vat
        return {
            "currency": "AOA",
            "subtotal": str(subtotal.quantize(Decimal("0.01"))),
            "vat": str(vat),
            "total": str(total.quantize(Decimal("0.01"))),
            "vat_rate_pct": 25,
            "billing_period": period,
            "price_fixed_aoa": fixed,
            "price_reference_aoa": reference,
            "price_promotional_aoa": promotional_aoa(code, period),  # type: ignore[arg-type]
            "promotion_applied": promo["active"],
            "promotion": promo,
        }

    def subscription_duration_days(self, billing_period: str) -> int:
        return BILLING_PERIOD_DAYS[billing_period]  # type: ignore[index]

    def recommendation_for(self, plan_code: str) -> dict | None:
        return PLAN_RECOMMENDATION.get(plan_code.strip().lower())
