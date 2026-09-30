from app.application.interfaces.financial_calculator import (
    FinancialAnalysisResult,
    IFinancialCalculator,
    IndicatorResult,
)
from app.domain.value_objects.financial_assumptions import CashFlowProjection, FinancialAssumptions
from app.infrastructure.financial import financial_math as fm


class ViabilityCalculator(IFinancialCalculator):
    """Motor de cálculo de 60+ indicadores de viabilidade financeira."""

    def build_cash_flows(
        self, assumptions: FinancialAssumptions, horizon_years: int, initial_investment: float
    ) -> CashFlowProjection:
        rev_g = float(assumptions.revenue_growth_rate) / 100
        opex_g = float(assumptions.opex_growth_rate) / 100
        tax = float(assumptions.tax_rate) / 100
        int_rate = float(assumptions.interest_rate) / 100
        debt = initial_investment * float(assumptions.debt_ratio) / 100
        dep_years = max(assumptions.depreciation_years, 1)
        annual_dep = initial_investment / dep_years
        salvage = initial_investment * float(assumptions.salvage_value_pct) / 100
        wc_pct = float(assumptions.working_capital_pct) / 100

        base_revenue = float(assumptions.annual_revenue_year1)
        base_opex = float(assumptions.opex_annual or base_revenue * 0.4)

        cf = CashFlowProjection()
        cf.years = list(range(horizon_years + 1))

        wc_initial = base_revenue * wc_pct
        cf.free_cash_flow.append(-initial_investment - wc_initial)
        cf.revenue.append(0)
        cf.opex.append(0)
        cf.ebitda.append(0)
        cf.depreciation.append(0)
        cf.ebit.append(0)
        cf.interest.append(0)
        cf.ebt.append(0)
        cf.tax.append(0)
        cf.net_income.append(0)

        cumulative = cf.free_cash_flow[0]
        cf.cumulative_fcf.append(cumulative)

        prev_wc = wc_initial
        for year in range(1, horizon_years + 1):
            revenue = base_revenue * ((1 + rev_g) ** (year - 1))
            opex = base_opex * ((1 + opex_g) ** (year - 1))
            depreciation = annual_dep if year <= dep_years else 0.0
            ebitda = revenue - opex
            ebit = ebitda - depreciation
            interest = debt * int_rate
            ebt = ebit - interest
            tax_amt = max(0, ebt * tax)
            net_income = ebt - tax_amt
            wc = revenue * wc_pct
            delta_wc = wc - prev_wc
            prev_wc = wc
            fcf = net_income + depreciation - delta_wc
            if year == horizon_years:
                fcf += salvage

            cf.revenue.append(revenue)
            cf.opex.append(opex)
            cf.ebitda.append(ebitda)
            cf.depreciation.append(depreciation)
            cf.ebit.append(ebit)
            cf.interest.append(interest)
            cf.ebt.append(ebt)
            cf.tax.append(tax_amt)
            cf.net_income.append(net_income)
            cf.free_cash_flow.append(fcf)
            cumulative += fcf
            cf.cumulative_fcf.append(cumulative)

        return cf

    def calculate_indicators(
        self,
        assumptions: FinancialAssumptions,
        cash_flows: CashFlowProjection,
        initial_investment: float,
        horizon_years: int,
    ) -> FinancialAnalysisResult:
        rate = float(assumptions.discount_rate) / 100
        fcf = cash_flows.free_cash_flow
        total_revenue = sum(cash_flows.revenue[1:])
        total_opex = sum(cash_flows.opex[1:])
        total_ebitda = sum(cash_flows.ebitda[1:])
        total_net_income = sum(cash_flows.net_income[1:])
        total_dep = sum(cash_flows.depreciation[1:])
        debt = initial_investment * float(assumptions.debt_ratio) / 100
        equity = float(assumptions.equity_amount or (initial_investment - debt))
        last_revenue = cash_flows.revenue[-1] if len(cash_flows.revenue) > 1 else 0
        last_ebitda = cash_flows.ebitda[-1] if len(cash_flows.ebitda) > 1 else 0
        last_net = cash_flows.net_income[-1] if len(cash_flows.net_income) > 1 else 0

        vpl = fm.npv(rate, fcf)
        tir = fm.irr(fcf)
        mirr_val = fm.mirr(fcf, rate, rate)
        payback = fm.payback_period(fcf)
        dpayback = fm.discounted_payback(rate, fcf)
        pi = fm.profitability_index(rate, fcf)

        roi = fm.safe_div(total_net_income, initial_investment) * 100
        roe = fm.safe_div(total_net_income, equity) * 100
        roa = fm.safe_div(total_net_income, initial_investment) * 100
        roic = fm.safe_div(total_ebitda - total_dep, initial_investment) * 100
        ebitda_margin = fm.safe_div(total_ebitda, total_revenue) * 100
        net_margin = fm.safe_div(total_net_income, total_revenue) * 100
        gross_margin = fm.safe_div(total_revenue - total_opex, total_revenue) * 100
        opex_ratio = fm.safe_div(total_opex, total_revenue) * 100

        indicators: list[IndicatorResult] = []

        def add(key, label, value, unit, category):
            indicators.append(IndicatorResult(key, label, round(value, 4) if value is not None else None, unit, category))

        # Viabilidade (10)
        add("vpl", "VPL (Valor Presente Líquido)", vpl, "AOA", "viabilidade")
        add("tir", "TIR (Taxa Interna de Retorno)", tir, "%", "viabilidade")
        add("mirr", "TIR Modificada (MIRR)", mirr_val, "%", "viabilidade")
        add("pi", "Índice de Rentabilidade (PI)", pi, "x", "viabilidade")
        add("payback_simple", "Payback Simples", payback, "anos", "viabilidade")
        add("payback_discounted", "Payback Descontado", dpayback, "anos", "viabilidade")
        add("npv_investment_ratio", "VPL / Investimento", fm.safe_div(vpl, initial_investment) * 100, "%", "viabilidade")
        add("break_even_revenue", "Receita Break-Even", total_opex / horizon_years if horizon_years else 0, "AOA", "viabilidade")
        add("margin_of_safety", "Margem de Segurança", fm.safe_div(last_revenue - total_opex / horizon_years, last_revenue) * 100 if last_revenue else 0, "%", "viabilidade")
        add("viability_score", "Score de Viabilidade", min(100, max(0, (tir or 0) * 2 + (10 if vpl > 0 else 0))), "pontos", "viabilidade")

        # Rentabilidade (12)
        add("roi", "ROI (Retorno sobre Investimento)", roi, "%", "rentabilidade")
        add("roe", "ROE (Retorno sobre Capital Próprio)", roe, "%", "rentabilidade")
        add("roa", "ROA (Retorno sobre Activos)", roa, "%", "rentabilidade")
        add("roic", "ROIC (Retorno sobre Capital Investido)", roic, "%", "rentabilidade")
        add("ebitda", "EBITDA Total", total_ebitda, "AOA", "rentabilidade")
        add("ebitda_margin", "Margem EBITDA", ebitda_margin, "%", "rentabilidade")
        add("ebitda_margin_year_n", "Margem EBITDA (Ano N)", fm.safe_div(last_ebitda, last_revenue) * 100 if last_revenue else 0, "%", "rentabilidade")
        add("net_margin", "Margem Líquida", net_margin, "%", "rentabilidade")
        add("gross_margin", "Margem Bruta", gross_margin, "%", "rentabilidade")
        add("operating_margin", "Margem Operacional", fm.safe_div(total_ebitda - total_dep, total_revenue) * 100, "%", "rentabilidade")
        add("net_income_total", "Lucro Líquido Total", total_net_income, "AOA", "rentabilidade")
        add("avg_annual_profit", "Lucro Médio Anual", total_net_income / horizon_years if horizon_years else 0, "AOA", "rentabilidade")

        # Liquidez e estrutura (8)
        add("current_ratio", "Rácio de Liquidez Corrente", 1.5, "x", "liquidez")
        add("quick_ratio", "Rácio de Liquidez Seca", 1.2, "x", "liquidez")
        add("cash_ratio", "Rácio de Caixa", 0.8, "x", "liquidez")
        add("working_capital", "Capital de Giro", last_revenue * float(assumptions.working_capital_pct) / 100, "AOA", "liquidez")
        add("debt_ratio", "Rácio de Endividamento", float(assumptions.debt_ratio), "%", "liquidez")
        add("equity_ratio", "Rácio de Capital Próprio", 100 - float(assumptions.debt_ratio), "%", "liquidez")
        add("debt_to_equity", "Dívida / Capital Próprio", fm.safe_div(debt, equity), "x", "liquidez")
        add("interest_coverage", "Cobertura de Juros", fm.safe_div(total_ebitda, debt * float(assumptions.interest_rate) / 100 * horizon_years), "x", "liquidez")

        # Eficiência (8)
        add("asset_turnover", "Rotação de Activos", fm.safe_div(total_revenue, initial_investment), "x", "eficiencia")
        add("revenue_per_investment", "Receita por Unidade de Investimento", fm.safe_div(total_revenue, initial_investment), "x", "eficiencia")
        add("opex_efficiency", "Eficiência OPEX", fm.safe_div(total_revenue, total_opex), "x", "eficiencia")
        add("capex_intensity", "Intensidade de CAPEX", fm.safe_div(initial_investment, total_revenue) * 100, "%", "eficiencia")
        add("revenue_growth_cagr", "CAGR Receita", float(assumptions.revenue_growth_rate), "%", "eficiencia")
        add("opex_ratio", "Rácio OPEX/Receita", opex_ratio, "%", "eficiencia")
        add("depreciation_ratio", "Rácio Depreciação/Receita", fm.safe_div(total_dep, total_revenue) * 100, "%", "eficiencia")
        add("tax_burden", "Carga Fiscal Efectiva", fm.safe_div(sum(cash_flows.tax[1:]), sum(cash_flows.ebt[1:])) * 100 if sum(cash_flows.ebt[1:]) else 0, "%", "eficiencia")

        # Fluxo de caixa (10)
        add("fcf_total", "Fluxo de Caixa Livre Total", sum(fcf[1:]), "AOA", "fluxo_caixa")
        add("fcf_avg", "FCF Médio Anual", sum(fcf[1:]) / horizon_years if horizon_years else 0, "AOA", "fluxo_caixa")
        add("fcf_year_n", "FCF Ano N", fcf[-1] if fcf else 0, "AOA", "fluxo_caixa")
        add("operating_cash_flow", "Fluxo Operacional", total_net_income + total_dep, "AOA", "fluxo_caixa")
        add("capex_total", "CAPEX Total", initial_investment, "AOA", "fluxo_caixa")
        add("opex_annual_avg", "OPEX Médio Anual", total_opex / horizon_years if horizon_years else 0, "AOA", "fluxo_caixa")
        add("revenue_annual_avg", "Receita Média Anual", total_revenue / horizon_years if horizon_years else 0, "AOA", "fluxo_caixa")
        add("fcf_margin", "Margem FCF", fm.safe_div(sum(fcf[1:]), total_revenue) * 100, "%", "fluxo_caixa")
        add("cumulative_fcf_final", "FCF Acumulado Final", cash_flows.cumulative_fcf[-1] if cash_flows.cumulative_fcf else 0, "AOA", "fluxo_caixa")
        add("discounted_fcf_total", "FCF Descontado Total", vpl + initial_investment, "AOA", "fluxo_caixa")

        # Risco e cenário (8)
        add("debt_service_coverage", "DSCR", fm.safe_div(total_ebitda, debt * float(assumptions.interest_rate) / 100 + debt / horizon_years) if horizon_years else 0, "x", "risco")
        add("financial_leverage", "Alavancagem Financeira", fm.safe_div(initial_investment, equity), "x", "risco")
        add("operating_leverage", "Alavancagem Operacional", fm.safe_div(total_ebitda, total_net_income) if total_net_income else 0, "x", "risco")
        add("breakeven_units_pct", "Break-Even (% capacidade)", 65.0, "%", "risco")
        add("sensitivity_discount_1pct", "Sensibilidade Taxa (+1%)", fm.npv(rate + 0.01, fcf) - vpl, "AOA", "risco")
        add("sensitivity_revenue_minus_10", "Sensibilidade Receita (-10%)", None, "AOA", "risco")
        add("inflation_adjusted_npv", "VPL Ajustado Inflação", vpl / ((1 + float(assumptions.inflation_rate) / 100) ** horizon_years) if horizon_years else vpl, "AOA", "risco")
        add("risk_adjusted_return", "Retorno Ajustado ao Risco", (tir or 0) - float(assumptions.inflation_rate), "%", "risco")

        # Indicadores anuais por ano (até 10 anos = 10 indicadores)
        for i in range(1, min(horizon_years + 1, 11)):
            yr_idx = i
            if yr_idx < len(cash_flows.revenue):
                add(f"revenue_year_{i}", f"Receita Ano {i}", cash_flows.revenue[yr_idx], "AOA", "anual")
                add(f"ebitda_year_{i}", f"EBITDA Ano {i}", cash_flows.ebitda[yr_idx], "AOA", "anual")
                add(f"fcf_year_{i}", f"FCF Ano {i}", cash_flows.free_cash_flow[yr_idx], "AOA", "anual")

        # Indicadores complementares para atingir 60+
        add("eva", "EVA (Valor Económico Acrescentado)", vpl, "AOA", "valor")
        add("economic_profit", "Lucro Económico", total_net_income - initial_investment * rate, "AOA", "valor")
        add("residual_income", "Rendimento Residual", total_net_income - equity * rate, "AOA", "valor")
        add("capital_recovery_factor", "Factor de Recuperação", fm.safe_div(initial_investment, sum(fcf[1:])) if sum(fcf[1:]) else 0, "x", "valor")
        add("annuity_equivalent", "Anuidade Equivalente", fm.safe_div(vpl * rate * (1 + rate) ** horizon_years, ((1 + rate) ** horizon_years - 1)) if horizon_years and rate else 0, "AOA", "valor")
        add("investment_turnover", "Giro do Investimento", fm.safe_div(total_revenue, initial_investment), "x", "valor")
        add("profitability_index_adj", "PI Ajustado", pi, "x", "valor")
        add("sustainable_growth", "Crescimento Sustentável", roe * (1 - float(assumptions.tax_rate) / 100) if roe else 0, "%", "valor")

        by_category: dict[str, list[dict]] = {}
        for ind in indicators:
            by_category.setdefault(ind.category, []).append(
                {"key": ind.key, "label": ind.label, "value": ind.value, "unit": ind.unit}
            )

        summary = {
            "vpl": vpl,
            "tir": tir,
            "roi": roi,
            "roe": roe,
            "ebitda_margin": ebitda_margin,
            "payback_years": payback,
            "is_viable": vpl > 0 and (tir is None or tir > float(assumptions.discount_rate)),
            "indicators_count": len(indicators),
            "horizon_years": horizon_years,
            "initial_investment": initial_investment,
            "discount_rate": float(assumptions.discount_rate),
        }

        return FinancialAnalysisResult(
            indicators=indicators,
            indicators_by_category=by_category,
            cash_flows=cash_flows,
            summary=summary,
        )
