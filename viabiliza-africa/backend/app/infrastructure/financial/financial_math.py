"""Funções matemáticas financeiras puras."""


def npv(rate: float, cash_flows: list[float]) -> float:
    if rate <= -1:
        return 0.0
    return sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cash_flows))


def irr(cash_flows: list[float], guess: float = 0.1) -> float | None:
    """TIR via método de bissecção."""
    if not cash_flows or all(cf >= 0 for cf in cash_flows) or all(cf <= 0 for cf in cash_flows):
        return None

    low, high = -0.99, 10.0
    for _ in range(200):
        mid = (low + high) / 2
        value = npv(mid, cash_flows)
        if abs(value) < 1e-6:
            return mid * 100
        if value > 0:
            low = mid
        else:
            high = mid
    result = (low + high) / 2
    return result * 100 if abs(npv(result, cash_flows)) < 1e4 else None


def mirr(cash_flows: list[float], finance_rate: float, reinvest_rate: float) -> float | None:
    if len(cash_flows) < 2:
        return None
    n = len(cash_flows) - 1
    pos = [cf if cf > 0 else 0 for cf in cash_flows]
    neg = [abs(cf) if cf < 0 else 0 for cf in cash_flows]
    pv_neg = sum(neg[t] / ((1 + finance_rate) ** t) for t in range(len(cash_flows)))
    fv_pos = sum(pos[t] * ((1 + reinvest_rate) ** (n - t)) for t in range(len(cash_flows)))
    if pv_neg == 0 or fv_pos == 0:
        return None
    return ((fv_pos / pv_neg) ** (1 / n) - 1) * 100


def payback_period(cash_flows: list[float]) -> float | None:
    cumulative = 0.0
    for t, cf in enumerate(cash_flows):
        prev = cumulative
        cumulative += cf
        if cumulative >= 0 and t > 0:
            if cf == 0:
                return float(t)
            fraction = abs(prev) / cf
            return t - 1 + fraction
    return None


def discounted_payback(rate: float, cash_flows: list[float]) -> float | None:
    cumulative = 0.0
    for t, cf in enumerate(cash_flows):
        dcf = cf / ((1 + rate) ** t)
        prev = cumulative
        cumulative += dcf
        if cumulative >= 0 and t > 0:
            if dcf == 0:
                return float(t)
            return t - 1 + abs(prev) / dcf
    return None


def profitability_index(rate: float, cash_flows: list[float]) -> float | None:
    initial = abs(cash_flows[0]) if cash_flows and cash_flows[0] < 0 else 0
    if initial == 0:
        return None
    pv_inflows = sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cash_flows) if t > 0 and cf > 0)
    pv_outflows = initial
    return pv_inflows / pv_outflows if pv_outflows else None


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    return a / b if b != 0 else default
