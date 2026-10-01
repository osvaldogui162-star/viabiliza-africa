"""Mapa de capacidades por plano — alinhado à página /planos e migration 011."""

from __future__ import annotations

from app.domain.entities.admin_config import SubscriptionPlan


def _limit_label(value: int | None, *, enabled: bool = True) -> str:
    if not enabled:
        return "—"
    if value is None:
        return "Ilimitado"
    return str(value)


def build_plan_capabilities(plan: SubscriptionPlan) -> dict:
    """Capacidades efectivas do plano para API e UI."""
    features = plan.features or {}
    scraping = bool(features.get("scraping"))
    max_scraping = features.get("max_scraping_items_monthly")
    esg_advanced = bool(features.get("esg_advanced"))
    esg_basic = bool(features.get("esg_basic"))

    return {
        "plan_code": plan.code,
        "plan_name": plan.name,
        "support_sla": features.get("support_sla"),
        "projects_limit": plan.max_projects,
        "projects_limit_label": _limit_label(plan.max_projects, enabled=True),
        "team_members_limit": plan.max_users,
        "team_members_limit_label": _limit_label(plan.max_users, enabled=True),
        "monte_carlo_iterations_limit": plan.max_monte_carlo_iterations,
        "scraping_enabled": scraping,
        "auto_ingestion_enabled": scraping,
        "scraping_monthly_limit": max_scraping if scraping else 0,
        "scraping_limit_label": (
            _limit_label(max_scraping, enabled=scraping) if scraping else "—"
        ),
        "monte_carlo_enabled": bool(features.get("monte_carlo", False)),
        "sensitivity_enabled": bool(features.get("sensitivity", False)),
        "reports_international": bool(features.get("reports_international")),
        "reports_bfa": bool(features.get("reports_bfa")),
        "reports_bda": bool(features.get("reports_bda")),
        "reports_aipex": bool(features.get("reports_aipex")),
        "bank_api_enabled": bool(features.get("bank_api")),
        "esg_enabled": esg_basic or esg_advanced,
        "esg_advanced_enabled": esg_advanced,
        "digital_twin_enabled": bool(features.get("digital_twin")),
        "sroi_enabled": bool(features.get("sroi")),
        "priority_support": bool(features.get("priority_support")),
        "erp_billing_integration": bool(features.get("erp_billing_integration")),
        "erp_auto_fiscal_invoice": bool(features.get("erp_auto_fiscal_invoice")),
    }
