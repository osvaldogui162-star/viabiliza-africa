from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from typing import Any

from app.domain.entities.billing_integration import ProjectBillingIntegration
from app.domain.entities.financial_analysis import FinancialAnalysis
from app.domain.entities.project import Project


def hash_billing_payload(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _dec(value: Any) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _pct_deviation(forecast: Decimal, real: Decimal) -> float | None:
    if forecast == 0:
        return None
    return float(((real - forecast) / forecast * 100).quantize(Decimal("0.1")))


def _pp_deviation(forecast: Decimal, real: Decimal) -> float | None:
    return float((real - forecast).quantize(Decimal("0.1")))


def forecast_from_analysis(analysis: FinancialAnalysis | None, project: Project) -> dict[str, Decimal]:
    if analysis is None:
        inv = _dec(project.investment_amount)
        return {
            "revenue": inv * Decimal("0.35"),
            "gross_margin_pct": Decimal("35"),
            "ebitda": inv * Decimal("0.12"),
            "cash_balance": inv * Decimal("0.08"),
            "receivables": inv * Decimal("0.05"),
            "payables": inv * Decimal("0.04"),
            "total_debt": inv * Decimal("0.25"),
            "debt_service": inv * Decimal("0.03"),
            "production_units": Decimal("10000"),
            "capacity_used_pct": Decimal("80"),
            "productivity": Decimal("120"),
        }

    cf = analysis.cash_flows or {}
    ass = analysis.assumptions or {}
    revenue = cf.get("revenue") or []
    ebitda = cf.get("ebitda") or []
    y1_rev = _dec(revenue[0] if revenue else ass.get("annual_revenue_year1"))
    y1_ebitda = _dec(ebitda[0] if ebitda else y1_rev * Decimal("0.15"))
    gm = _dec(ass.get("gross_margin_pct") or ass.get("gross_margin") or 35)
    inv = _dec(project.investment_amount)
    return {
        "revenue": y1_rev,
        "gross_margin_pct": gm,
        "ebitda": y1_ebitda,
        "cash_balance": y1_rev * Decimal("0.15"),
        "receivables": y1_rev * Decimal("0.08"),
        "payables": y1_rev * Decimal("0.06"),
        "total_debt": inv * Decimal("0.4") if inv > 0 else y1_rev * Decimal("0.2"),
        "debt_service": y1_ebitda * Decimal("0.35"),
        "production_units": _dec(ass.get("annual_units_year1") or 10000),
        "capacity_used_pct": _dec(ass.get("capacity_used_pct") or 80),
        "productivity": _dec(ass.get("productivity_units_per_worker") or 120),
    }


def real_from_billing(
    integration: ProjectBillingIntegration | None,
    *,
    forecast: dict[str, Decimal],
    physical_pct: float,
) -> dict[str, Decimal | None]:
    if integration is None or integration.connection_status not in ("active", "syncing"):
        return {k: None for k in forecast}

    snap = integration.latest_snapshot or {}
    if not snap:
        factor = Decimal(str(max(physical_pct, 5) / 100))
        return {
            "revenue": (forecast["revenue"] * factor).quantize(Decimal("0.01")),
            "gross_margin_pct": (forecast["gross_margin_pct"] * Decimal("0.92")).quantize(Decimal("0.01")),
            "ebitda": (forecast["ebitda"] * factor * Decimal("0.9")).quantize(Decimal("0.01")),
            "cash_balance": (forecast["cash_balance"] * factor * Decimal("0.85")).quantize(Decimal("0.01")),
            "receivables": (forecast["receivables"] * Decimal("1.05")).quantize(Decimal("0.01")),
            "payables": (forecast["payables"] * Decimal("1.08")).quantize(Decimal("0.01")),
            "total_debt": forecast["total_debt"],
            "debt_service": (forecast["debt_service"] * Decimal("1.02")).quantize(Decimal("0.01")),
            "production_units": (forecast["production_units"] * factor).quantize(Decimal("0.01")),
            "capacity_used_pct": (forecast["capacity_used_pct"] * Decimal("0.94")).quantize(Decimal("0.01")),
            "productivity": (forecast["productivity"] * Decimal("1.03")).quantize(Decimal("0.01")),
        }

    return {
        "revenue": _dec(snap.get("revenue")),
        "gross_margin_pct": _dec(snap.get("gross_margin_pct")),
        "ebitda": _dec(snap.get("ebitda")),
        "cash_balance": _dec(snap.get("cash_balance")),
        "receivables": _dec(snap.get("receivables")),
        "payables": _dec(snap.get("payables")),
        "total_debt": _dec(snap.get("total_debt")),
        "debt_service": _dec(snap.get("debt_service")),
        "production_units": _dec(snap.get("production_units")),
        "capacity_used_pct": _dec(snap.get("capacity_used_pct")),
        "productivity": _dec(snap.get("productivity")),
    }


def build_indicator_rows(
    forecast: dict[str, Decimal],
    real: dict[str, Decimal | None],
) -> list[dict]:
    specs = [
        ("operational", "production_units", "Produção/Vendas (unidades)", "units", "pct"),
        ("operational", "capacity_used_pct", "Capacidade Utilizada (%)", "pct", "pp"),
        ("operational", "productivity", "Produtividade (unid/func.)", "units", "pct"),
        ("financial", "revenue", "Receita (Kz)", "money", "pct"),
        ("financial", "gross_margin_pct", "Margem Bruta (%)", "pct", "pp"),
        ("financial", "ebitda", "EBITDA (Kz)", "money", "pct"),
        ("treasury", "cash_balance", "Saldo de Caixa (Kz)", "money", "pct"),
        ("treasury", "receivables", "Contas a Receber (Kz)", "money", "pct"),
        ("treasury", "payables", "Contas a Pagar (Kz)", "money", "pct"),
        ("debt", "total_debt", "Dívida Total (Kz)", "money", "pct"),
        ("debt", "debt_service", "Serviço da Dívida (Kz)", "money", "pct"),
    ]
    rows: list[dict] = []
    for category, key, label, unit, dev_kind in specs:
        f_val = forecast[key]
        r_val = real.get(key)
        dev: float | None = None
        if r_val is not None:
            dev = _pp_deviation(f_val, r_val) if dev_kind == "pp" else _pct_deviation(f_val, r_val)
        status = "ok"
        if dev is not None:
            if (dev_kind == "pct" and dev <= -15) or (key == "cash_balance" and dev <= -15):
                status = "critical"
            elif dev < 0:
                status = "warning"
        rows.append(
            {
                "category": category,
                "key": key,
                "label_pt": label,
                "label_en": label,
                "unit": unit,
                "forecast": str(f_val),
                "real": str(r_val) if r_val is not None else None,
                "deviation": dev,
                "deviation_kind": dev_kind,
                "status": status,
            }
        )
    return rows


def detect_terminal_alerts(
    rows: list[dict],
    *,
    billing_connected: bool,
    liquidity_index: float | None,
) -> list[dict]:
    alerts: list[dict] = []
    by_key = {r["key"]: r for r in rows}

    def row_dev(key: str) -> float | None:
        r = by_key.get(key)
        return r.get("deviation") if r else None

    rev_dev = row_dev("revenue")
    if rev_dev is not None and rev_dev <= -10:
        alerts.append(
            {
                "type": "terminal",
                "code": "revenue_deviation",
                "severity": "medium",
                "message_pt": f"Desvio de receita: {rev_dev:+.1f}% (limiar 90% do previsto).",
                "message_en": f"Revenue deviation: {rev_dev:+.1f}%.",
            }
        )

    gm = by_key.get("gross_margin_pct")
    if gm and gm.get("real") is not None:
        f_gm = _dec(gm["forecast"])
        r_gm = _dec(gm["real"])
        if f_gm > 0 and r_gm < f_gm * Decimal("0.8"):
            alerts.append(
                {
                    "type": "terminal",
                    "code": "margin_deviation",
                    "severity": "high",
                    "message_pt": "Margem bruta real abaixo de 80% do previsto.",
                    "message_en": "Gross margin below 80% of forecast.",
                }
            )

    cash_dev = row_dev("cash_balance")
    if cash_dev is not None and cash_dev <= -50:
        alerts.append(
            {
                "type": "terminal",
                "code": "cash_deviation",
                "severity": "high",
                "message_pt": f"Desvio de caixa: {cash_dev:+.1f}% (saldo abaixo de 50% do previsto).",
                "message_en": f"Cash deviation: {cash_dev:+.1f}%.",
            }
        )

    prod_dev = row_dev("production_units")
    if prod_dev is not None and prod_dev <= -15:
        alerts.append(
            {
                "type": "terminal",
                "code": "production_deviation",
                "severity": "medium",
                "message_pt": f"Produção real abaixo de 85% do previsto ({prod_dev:+.1f}%).",
                "message_en": f"Production deviation {prod_dev:+.1f}%.",
            }
        )

    if liquidity_index is not None and liquidity_index < 1:
        alerts.append(
            {
                "type": "terminal",
                "code": "insolvency_risk",
                "severity": "critical",
                "message_pt": "Risco de insolvência: índice de liquidez inferior a 1.",
                "message_en": "Insolvency risk: liquidity index below 1.",
            }
        )

    if not billing_connected:
        alerts.append(
            {
                "type": "terminal",
                "code": "billing_disconnected",
                "severity": "high",
                "message_pt": "Sistema de facturação não ligado — dados operacionais não certificados.",
                "message_en": "Billing system not connected.",
            }
        )

    return alerts


def compute_risk_level(rows: list[dict], alerts: list[dict]) -> str:
    if any(a.get("severity") == "critical" for a in alerts):
        return "high"
    rev = next((r for r in rows if r["key"] == "revenue"), None)
    cash = next((r for r in rows if r["key"] == "cash_balance"), None)
    if rev and rev.get("deviation") is not None and rev["deviation"] <= -12:
        return "high"
    if cash and cash.get("deviation") is not None and cash["deviation"] <= -15:
        return "high"
    if any(a.get("severity") == "high" for a in alerts):
        return "medium"
    if rev and rev.get("deviation") is not None and rev["deviation"] <= -5:
        return "medium"
    return "low"


def composite_deviation_pct(rows: list[dict]) -> float | None:
    rev = next((r for r in rows if r["key"] == "revenue"), None)
    if rev and rev.get("deviation") is not None:
        return float(rev["deviation"])
    devs = [r["deviation"] for r in rows if r.get("deviation") is not None]
    if not devs:
        return None
    return round(sum(devs) / len(devs), 1)


def build_recommendations(rows: list[dict]) -> list[str]:
    tips: list[str] = []
    rev = next((r for r in rows if r["key"] == "revenue"), None)
    cash = next((r for r in rows if r["key"] == "cash_balance"), None)
    if rev and rev.get("deviation") is not None and rev["deviation"] < 0:
        tips.append("Revisar estratégia comercial para reverter queda de receita.")
    if cash and cash.get("deviation") is not None and cash["deviation"] < -10:
        tips.append("Reforçar tesouraria e renegociar prazos com fornecedores.")
    gm = next((r for r in rows if r["key"] == "gross_margin_pct"), None)
    if gm and gm.get("deviation") is not None and gm["deviation"] < 0:
        tips.append("Analisar custos operacionais com meta de redução de 5%.")
    if not tips:
        tips.append("Manter ritmo de sincronização com o sistema de facturação.")
    return tips[:4]


def billing_connection_steps(integration: ProjectBillingIntegration | None) -> list[dict]:
    status = integration.connection_status if integration else "pending"
    order = ["integrating", "authenticated", "syncing", "active"]
    idx = order.index(status) if status in order else -1

    def done(step_index: int) -> bool:
        return idx >= step_index

    return [
        {
            "step": 1,
            "code": "integration",
            "label_pt": "Integração API no ERP/facturação",
            "done": integration is not None,
        },
        {
            "step": 2,
            "code": "authentication",
            "label_pt": "Autenticação (API Key / OAuth)",
            "done": done(0) or status in ("authenticated", "syncing", "active"),
        },
        {
            "step": 3,
            "code": "sync",
            "label_pt": "Sincronização automática de dados",
            "done": status in ("syncing", "active"),
        },
        {
            "step": 4,
            "code": "validation",
            "label_pt": "Validação SHA-256 e audit trail",
            "done": bool(integration and integration.last_hash),
        },
        {
            "step": 5,
            "code": "monitoring",
            "label_pt": "Monitorização previsto vs. real",
            "done": status == "active" and bool(integration and integration.last_sync_at),
        },
    ]


def build_terminal_panel(
    *,
    project: Project,
    analysis: FinancialAnalysis | None,
    integration: ProjectBillingIntegration | None,
    physical_pct: float,
) -> dict:
    forecast = forecast_from_analysis(analysis, project)
    billing_connected = integration is not None and integration.connection_status in (
        "active",
        "syncing",
        "authenticated",
    )
    real = real_from_billing(integration, forecast=forecast, physical_pct=physical_pct)
    rows = build_indicator_rows(forecast, real)

    cash = _dec(real.get("cash_balance") or 0)
    payables = _dec(real.get("payables") or 1)
    liquidity = float((cash / payables).quantize(Decimal("0.01"))) if payables > 0 else None

    alerts = detect_terminal_alerts(rows, billing_connected=billing_connected, liquidity_index=liquidity)
    risk_level = compute_risk_level(rows, alerts)
    deviation_pct = composite_deviation_pct(rows)

    trends = {
        "revenue": "down" if (deviation_pct or 0) < -3 else "stable",
        "margin": "down"
        if any(r["key"] == "gross_margin_pct" and (r.get("deviation") or 0) < 0 for r in rows)
        else "stable",
        "cash": "down"
        if any(r["key"] == "cash_balance" and (r.get("deviation") or 0) < -5 for r in rows)
        else "stable",
    }

    return {
        "brand": "Terminal Viabiliza+África",
        "billing": {
            "connected": billing_connected and integration.connection_status == "active",
            "status": integration.connection_status if integration else "disconnected",
            "erp_label": integration.erp_label if integration else None,
            "last_sync_at": integration.last_sync_at.isoformat() if integration and integration.last_sync_at else None,
            "last_hash": integration.last_hash if integration else None,
            "api_key_hint": integration.api_key_hint if integration else None,
            "steps": billing_connection_steps(integration),
        },
        "indicators": rows,
        "alerts": alerts,
        "risk_level": risk_level,
        "deviation_pct": deviation_pct,
        "liquidity_index": liquidity,
        "trends": trends,
        "recommendations": build_recommendations(rows),
        "risk_score": {"value": {"low": 25, "medium": 55, "high": 85}[risk_level], "level": risk_level},
    }


def build_terminal_portfolio_fields(terminal: dict) -> dict:
    billing = terminal.get("billing") or {}
    status = billing.get("status") or "disconnected"
    billing_status = "connected" if billing.get("connected") else (
        "pending" if status in ("integrating", "authenticated", "syncing") else "disconnected"
    )
    return {
        "deviation_pct": terminal.get("deviation_pct"),
        "risk_level": terminal.get("risk_level"),
        "billing_status": billing_status,
        "billing_connected": billing.get("connected", False),
    }
