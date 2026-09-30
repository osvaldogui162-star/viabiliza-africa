"""Matriz de funcionalidades por plano — fonte única para catálogo, sync e regras UC39."""

from __future__ import annotations

from typing import Any


def reports_flags(*, full: bool = False, international_only: bool = False) -> dict[str, bool]:
    if international_only:
        return {
            "reports_international": True,
            "reports_bfa": False,
            "reports_bda": False,
            "reports_aipex": False,
        }
    if full:
        return {
            "reports_international": True,
            "reports_bfa": True,
            "reports_bda": True,
            "reports_aipex": True,
        }
    return {
        "reports_international": False,
        "reports_bfa": False,
        "reports_bda": False,
        "reports_aipex": False,
    }


def analysis_flags(*, monte_carlo: bool = True, sensitivity: bool = True) -> dict[str, bool]:
    return {"monte_carlo": monte_carlo, "sensitivity": sensitivity}


def esg_flags(*, basic: bool = False, advanced: bool = False) -> dict[str, bool]:
    return {"esg_basic": basic, "esg_advanced": advanced}


def commercial_feature_overrides(code: str) -> dict[str, Any]:
    """Flags comerciais partilhadas (alinhado a /planos e migration 011)."""
    if code == "free":
        return {
            **reports_flags(international_only=True),
            **analysis_flags(),
            **esg_flags(),
            "scraping": False,
            "max_scraping_items_monthly": 0,
            "bank_api": False,
            "digital_twin": False,
            "sroi": False,
            "priority_support": False,
            "contact_only": False,
            "hidden_from_pricing": True,
            "plan_tier": "internal",
        }
    if code == "starter":
        return {
            **reports_flags(full=True),
            **analysis_flags(),
            **esg_flags(basic=True),
            "scraping": True,
            "max_scraping_items_monthly": 50,
            "bank_api": False,
            "digital_twin": True,
            "sroi": False,
            "priority_support": False,
            "contact_only": False,
            "plan_tier": "main",
            "emoji": "🚀",
            "popular": True,
        }
    if code == "business":
        return {
            **reports_flags(full=True),
            **analysis_flags(),
            **esg_flags(basic=True, advanced=True),
            "scraping": True,
            "max_scraping_items_monthly": 500,
            "bank_api": True,
            "digital_twin": True,
            "sroi": True,
            "priority_support": True,
            "contact_only": False,
            "plan_tier": "main",
            "emoji": "🏢",
            "popular": False,
        }
    if code == "enterprise":
        return {
            **reports_flags(full=True),
            **analysis_flags(),
            **esg_flags(basic=True, advanced=True),
            "scraping": True,
            "max_scraping_items_monthly": None,
            "bank_api": True,
            "digital_twin": True,
            "sroi": True,
            "priority_support": True,
            "onboarding": True,
            "consulting": True,
            "contact_only": True,
            "plan_tier": "main",
            "emoji": "👑",
            "popular": False,
        }
    if code == "academia_institutional":
        return {
            **reports_flags(full=True),
            **analysis_flags(),
            **esg_flags(basic=True, advanced=True),
            "scraping": True,
            "max_scraping_items_monthly": None,
            "bank_api": True,
            "digital_twin": True,
            "sroi": True,
            "priority_support": True,
            "yearly_only": False,
            "contact_only": True,
            "plan_tier": "special",
            "emoji": "🏛️",
            "popular": False,
        }
    if code == "government":
        return {
            **reports_flags(full=True),
            **analysis_flags(),
            **esg_flags(basic=True, advanced=True),
            "scraping": True,
            "max_scraping_items_monthly": None,
            "bank_api": True,
            "digital_twin": True,
            "sroi": True,
            "priority_support": True,
            "onboarding": True,
            "custom_pricing": True,
            "contact_only": True,
            "plan_tier": "special",
            "emoji": "🏛️",
            "popular": False,
        }
    raise KeyError(f"Plano desconhecido: {code}")
