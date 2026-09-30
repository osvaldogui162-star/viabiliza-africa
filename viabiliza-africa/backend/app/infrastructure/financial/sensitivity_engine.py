from app.application.interfaces.financial_calculator import IFinancialCalculator
from app.application.interfaces.sensitivity_engine import (
    ISensitivityEngine,
    SensitivityResult,
    SensitivityVariable,
)
from app.domain.value_objects.financial_assumptions import FinancialAssumptions
from app.infrastructure.financial import financial_math as fm


class TornadoSensitivityEngine(ISensitivityEngine):
    """Análise de sensibilidade tipo tornado (UC21)."""

    def __init__(self, calculator: IFinancialCalculator) -> None:
        self._calculator = calculator

    def analyze(
        self,
        assumptions: FinancialAssumptions,
        horizon_years: int,
        initial_investment: float,
        variables: list[SensitivityVariable],
    ) -> SensitivityResult:
        if len(variables) < self.MIN_VARIABLES or len(variables) > self.MAX_VARIABLES:
            raise ValueError(
                f"Variáveis devem estar entre {self.MIN_VARIABLES} e {self.MAX_VARIABLES}"
            )

        base_cf = self._calculator.build_cash_flows(assumptions, horizon_years, initial_investment)
        rate = float(assumptions.discount_rate) / 100
        base_npv = fm.npv(rate, base_cf.free_cash_flow)
        base_irr = fm.irr(base_cf.free_cash_flow)

        tornado_npv: list[dict] = []
        tornado_irr: list[dict] = []
        var_details: list[dict] = []

        for var in variables:
            low_assump = self._apply_shock(assumptions, var.key, var.shock_low_pct)
            high_assump = self._apply_shock(assumptions, var.key, var.shock_high_pct)

            low_cf = self._calculator.build_cash_flows(low_assump, horizon_years, initial_investment)
            high_cf = self._calculator.build_cash_flows(
                high_assump, horizon_years, initial_investment
            )

            low_npv = fm.npv(rate, low_cf.free_cash_flow)
            high_npv = fm.npv(rate, high_cf.free_cash_flow)
            low_irr = fm.irr(low_cf.free_cash_flow)
            high_irr = fm.irr(high_cf.free_cash_flow)

            npv_range = max(abs(low_npv - base_npv), abs(high_npv - base_npv))
            irr_range = 0.0
            if base_irr is not None and low_irr is not None and high_irr is not None:
                irr_range = max(abs(low_irr - base_irr), abs(high_irr - base_irr))

            tornado_npv.append(
                {
                    "key": var.key,
                    "label": var.label,
                    "low_npv": round(low_npv, 2),
                    "high_npv": round(high_npv, 2),
                    "base_npv": round(base_npv, 2),
                    "impact": round(npv_range, 2),
                }
            )
            tornado_irr.append(
                {
                    "key": var.key,
                    "label": var.label,
                    "low_irr": low_irr,
                    "high_irr": high_irr,
                    "base_irr": base_irr,
                    "impact": round(irr_range, 4),
                }
            )
            var_details.append(
                {
                    "key": var.key,
                    "label": var.label,
                    "base_value": var.base_value,
                    "shock_low_pct": var.shock_low_pct,
                    "shock_high_pct": var.shock_high_pct,
                }
            )

        tornado_npv.sort(key=lambda x: x["impact"], reverse=True)
        tornado_irr.sort(key=lambda x: x["impact"], reverse=True)

        return SensitivityResult(
            variables=var_details,
            base_npv=round(base_npv, 2),
            base_irr=base_irr,
            tornado_npv=tornado_npv,
            tornado_irr=tornado_irr,
        )

    def _apply_shock(
        self, assumptions: FinancialAssumptions, key: str, shock_pct: float
    ) -> FinancialAssumptions:
        data = assumptions.to_dict()
        if key not in data or data[key] is None:
            return assumptions
        val = float(data[key])
        data[key] = str(val * (1 + shock_pct / 100))
        return FinancialAssumptions.from_dict(data)
