"""Taxas de câmbio MVP centralizadas (AOA, USD, EUR)."""

from __future__ import annotations

from decimal import Decimal

SUPPORTED_CURRENCIES: frozenset[str] = frozenset({"AOA", "USD", "EUR"})
DEFAULT_CURRENCY = "AOA"

# Taxas institucionais aproximadas para relatórios e dashboards
FX_RATES: dict[tuple[str, str], float] = {
    ("AOA", "USD"): 1 / 850,
    ("AOA", "EUR"): 1 / 920,
    ("USD", "AOA"): 850,
    ("EUR", "AOA"): 920,
    ("USD", "EUR"): 0.92,
    ("EUR", "USD"): 1.09,
}


def normalize_currency(code: str | None, *, default: str = DEFAULT_CURRENCY) -> str:
    normalized = (code or default).upper()
    if normalized not in SUPPORTED_CURRENCIES:
        return default
    return normalized


def fx_rate(from_currency: str, to_currency: str) -> float:
    source = normalize_currency(from_currency)
    target = normalize_currency(to_currency)
    if source == target:
        return 1.0
    return FX_RATES.get((source, target), 1.0)


def convert_amount(
    amount: Decimal | float | int,
    from_currency: str,
    to_currency: str,
) -> float:
    value = float(amount)
    return value * fx_rate(from_currency, to_currency)
