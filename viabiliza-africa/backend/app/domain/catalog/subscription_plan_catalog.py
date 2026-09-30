"""Catálogo comercial alinhado à página /planos (5 pacotes + free interno)."""

from decimal import Decimal

from app.domain.catalog.plan_commercial_pricing import PLAN_AOA_PRICING, aoa_to_usd_display
from app.domain.catalog.plan_feature_matrix import commercial_feature_overrides


def _aoa_features(code: str, extra: dict) -> dict:
    base = {
        **extra,
        "billing_periods": ["quarterly", "semiannual", "yearly"],
    }
    pricing = PLAN_AOA_PRICING.get(code)
    if pricing is None:
        return {
            **base,
            "price_quarterly_aoa": 0,
            "price_semiannual_aoa": 0,
            "price_yearly_aoa": 0,
            "reference_quarterly_aoa": 0,
            "reference_semiannual_aoa": 0,
            "reference_yearly_aoa": 0,
        }
    return {
        **base,
        "price_quarterly_aoa": pricing["quarterly"]["fixed"],
        "price_semiannual_aoa": pricing["semiannual"]["fixed"],
        "price_yearly_aoa": pricing["yearly"]["fixed"],
        "reference_quarterly_aoa": pricing["quarterly"]["reference"],
        "reference_semiannual_aoa": pricing["semiannual"]["reference"],
        "reference_yearly_aoa": pricing["yearly"]["reference"],
    }


def _features(code: str, *, support_sla: str) -> dict:
    return _aoa_features(code, {**commercial_feature_overrides(code), "support_sla": support_sla})


SUBSCRIPTION_PLAN_CATALOG: list[dict] = [
    {
        "code": "free",
        "name": "Gratuito",
        "description": "Plano inicial interno para experimentar a plataforma",
        "price_monthly": Decimal("0"),
        "price_yearly": Decimal("0"),
        "currency": "AOA",
        "max_projects": 3,
        "max_users": 1,
        "max_monte_carlo_iterations": 1000,
        "display_order": 0,
        "features": {
            **_features("free", support_sla="Email (72h)"),
            "price_quarterly_aoa": 0,
            "price_semiannual_aoa": 0,
            "price_yearly_aoa": 0,
        },
    },
    {
        "code": "starter",
        "name": "Starter",
        "description": "Para PMEs e consultores individuais",
        "price_monthly": aoa_to_usd_display(PLAN_AOA_PRICING["starter"]["quarterly"]["fixed"]),
        "price_yearly": aoa_to_usd_display(PLAN_AOA_PRICING["starter"]["yearly"]["fixed"]),
        "currency": "AOA",
        "max_projects": 20,
        "max_users": 1,
        "max_monte_carlo_iterations": 10000,
        "display_order": 1,
        "features": _features("starter", support_sla="Email (48h)"),
    },
    {
        "code": "business",
        "name": "Business",
        "description": "Para empresas e consultorias de médio porte",
        "price_monthly": aoa_to_usd_display(PLAN_AOA_PRICING["business"]["quarterly"]["fixed"]),
        "price_yearly": aoa_to_usd_display(PLAN_AOA_PRICING["business"]["yearly"]["fixed"]),
        "currency": "AOA",
        "max_projects": None,
        "max_users": 5,
        "max_monte_carlo_iterations": 50000,
        "display_order": 2,
        "features": _features("business", support_sla="Prioritário (24h)"),
    },
    {
        "code": "enterprise",
        "name": "Enterprise",
        "description": "Para grandes empresas, bancos e organizações",
        "price_monthly": aoa_to_usd_display(PLAN_AOA_PRICING["enterprise"]["quarterly"]["fixed"]),
        "price_yearly": aoa_to_usd_display(PLAN_AOA_PRICING["enterprise"]["yearly"]["fixed"]),
        "currency": "AOA",
        "max_projects": None,
        "max_users": None,
        "max_monte_carlo_iterations": 50000,
        "display_order": 3,
        "features": _features("enterprise", support_sla="Dedicado (4h)"),
    },
    {
        "code": "academia_institutional",
        "name": "Academia Institucional",
        "description": "Para universidades, faculdades e centros de investigação",
        "price_monthly": aoa_to_usd_display(
            PLAN_AOA_PRICING["academia_institutional"]["quarterly"]["fixed"]
        ),
        "price_yearly": aoa_to_usd_display(
            PLAN_AOA_PRICING["academia_institutional"]["yearly"]["fixed"]
        ),
        "currency": "AOA",
        "max_projects": None,
        "max_users": 50,
        "max_monte_carlo_iterations": 50000,
        "display_order": 4,
        "features": _features("academia_institutional", support_sla="Prioritário"),
    },
    {
        "code": "government",
        "name": "Governo",
        "description": "Para instituições públicas e governamentais",
        "price_monthly": aoa_to_usd_display(PLAN_AOA_PRICING["government"]["quarterly"]["fixed"]),
        "price_yearly": aoa_to_usd_display(PLAN_AOA_PRICING["government"]["yearly"]["fixed"]),
        "currency": "AOA",
        "max_projects": None,
        "max_users": None,
        "max_monte_carlo_iterations": 50000,
        "display_order": 5,
        "features": _features("government", support_sla="24/7"),
    },
]

DEPRECATED_PLAN_CODES = frozenset({"academic", "social_impact", "professional"})
