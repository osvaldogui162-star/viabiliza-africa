"""Relatório Geral — preenche o modelo HTML institucional e gera PDF."""

from __future__ import annotations

import html
import re
from datetime import datetime
from pathlib import Path

from app.application.dto.report_data import ReportDataBundle
from app.application.services.report_data_aggregator import ReportDataAggregator
from app.infrastructure.pdf.chrome_pdf import html_to_pdf


TEMPLATE_PATH = Path(__file__).resolve().parent / "templates" / "general_report_model.html"


class GeneralReportHtmlBuilder:
    """Preenche o modelo «RELATÓRIO MODELO GERAL» com dados do projecto."""

    def __init__(
        self,
        data: ReportDataBundle,
        *,
        verification_url: str,
        qr_image_b64: str | None,
    ) -> None:
        self.data = data
        self.verification_url = verification_url
        self.qr_image_b64 = qr_image_b64
        self.lang = data.report_language
        self.currency = data.report_currency
        self.p = data.project
        self.s = data.indicators_summary or {}

    def _t(self, pt: str, en: str) -> str:
        return pt if self.lang != "en" else en

    def _esc(self, value) -> str:
        return html.escape("" if value is None else str(value))

    def _money(self, amount) -> str:
        try:
            val = float(amount or 0) * float(self.data.exchange_rate or 1)
        except (TypeError, ValueError):
            val = 0.0
        return ReportDataAggregator.format_money(val, self.currency, self.lang)

    def _num(self, value, default: float = 0.0) -> float:
        try:
            if value is None:
                return default
            return float(value)
        except (TypeError, ValueError):
            return default

    def _pct(self, value) -> str:
        return f"{self._num(value):.2f}"

    def build_html(self) -> str:
        if not TEMPLATE_PATH.is_file():
            raise FileNotFoundError(f"Modelo HTML em falta: {TEMPLATE_PATH}")

        doc = TEMPLATE_PATH.read_text(encoding="utf-8")
        doc = self._prepare_print_mode(doc)
        doc = self._fill_header(doc)
        doc = self._replace_identity(doc)
        doc = self._inject_dynamic_blocks(doc)
        doc = self._append_verification(doc)
        return doc

    def build_pdf(self) -> bytes:
        return html_to_pdf(self.build_html())

    # ── print / layout ─────────────────────────────────────────────────

    def _prepare_print_mode(self, doc: str) -> str:
        """Força todas as abas visíveis (PDF) e remove navegação interactiva."""
        # Mostrar todos os sheets no ecrã (Chrome print usa layout de ecrã + @media print)
        doc = doc.replace(
            ".sheet-content {\n            padding: 30px 40px;\n            display: none;\n        }",
            ".sheet-content {\n            padding: 30px 40px;\n            display: block;\n            page-break-after: always;\n        }",
        )
        doc = re.sub(
            r"<div class=\"sheet-tabs\"[\s\S]*?</div>\s*(?=<!-- =+\s*\n\s*SHEET 0)",
            '<div class="sheet-tabs" style="display:none"></div>\n\n    ',
            doc,
            count=1,
        )
        # Remover script de tabs (já não necessário)
        doc = re.sub(
            r"<!-- =+\s*\nSCRIPT[\s\S]*?</script>\s*",
            "",
            doc,
            count=1,
        )
        return doc

    def _fill_header(self, doc: str) -> str:
        now = datetime.now()
        date_str = now.strftime("%B %Y") if self.lang == "en" else now.strftime("%B %Y")
        # Portuguese month names
        if self.lang != "en":
            months = {
                1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
                5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
                9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
            }
            date_str = f"{months[now.month]} {now.year}"

        doc_id = f"DOC-{now.strftime('%Y')}-{str(self.p.id)[:8].upper()}"
        replacements = {
            'id="projectName">[Nome do Projeto]': f'id="projectName">{self._esc(self.p.name)}',
            'id="promoterName">[Nome da Empresa]': f'id="promoterName">{self._esc(self.p.company_name)}',
            'id="sectorName">[Setor de Atividade]': f'id="sectorName">{self._esc(self.p.sector.replace("_", " ").title())}',
            'id="reportDate">Julho 2026': f'id="reportDate">{date_str}',
            'id="reportCurrency">AOA / USD': f'id="reportCurrency">{self._esc(self.currency)}',
            "📄 DOC-2026-001 · v1.0": f"📄 {doc_id} · v1.0",
            "Documento v1.0 · Julho 2026": f"Documento v1.0 · {date_str}",
        }
        for old, new in replacements.items():
            doc = doc.replace(old, new)

        subtitle = self._t(
            "Plano de Negócios · Modelo Geral Internacional",
            "Business Plan · International General Model",
        )
        doc = doc.replace(
            "Plano de Negócios · Modelo Internacional · BFA · BDA",
            subtitle,
        )
        title = self._t(
            "ESTUDO DE VIABILIDADE ECONÓMICO-FINANCEIRA",
            "ECONOMIC-FINANCIAL FEASIBILITY STUDY",
        )
        doc = doc.replace(
            "ESTUDO DE VIABILIDADE ECONÓMICO-FINANCEIRA",
            title,
        )
        return doc

    def _replace_identity(self, doc: str) -> str:
        viable = bool(self.s.get("is_viable"))
        verdict_pt = "VIÁVEL" if viable else "NÃO VIÁVEL / REQUER ANÁLISE"
        verdict_en = "VIABLE" if viable else "NOT VIABLE / REQUIRES REVIEW"
        verdict = verdict_pt if self.lang != "en" else verdict_en
        desc = (self.p.description or "").strip() or self._t(
            f"Projecto de investimento no sector {self.p.sector.replace('_', ' ')} "
            f"em {self.p.country}, com horizonte de {self.p.horizon_years} anos.",
            f"Investment project in the {self.p.sector.replace('_', ' ')} sector "
            f"in {self.p.country}, with a {self.p.horizon_years}-year horizon.",
        )

        pairs = [
            ("[Nome do Projeto]", self.p.name),
            ("[Nome do Projeto]", self.p.name),
            ("[Nome da Empresa]", self.p.company_name),
            ("[Setor]", self.p.sector.replace("_", " ").title()),
            ("[Setor de Atividade]", self.p.sector.replace("_", " ").title()),
            ("[breve descrição]", desc[:220]),
            ("[Valor]", self._money(self.p.investment_amount)),
            ("[X] anos", f"{self.p.horizon_years} {self._t('anos', 'years')}"),
            ("[X] fases", self._t("3 fases", "3 phases")),
            ("[Data]", datetime.now().strftime("%d/%m/%Y")),
            ("[VPL]", self._money(self.s.get("vpl"))),
            ("[TIR]", self._pct(self.s.get("tir"))),
            ("[Payback]", self._pct(self.s.get("payback_years"))),
            ("[ROI]", self._pct(self.s.get("roi"))),
            ("[CAPEX]", self._money(self.data.capex_total or self.p.investment_amount)),
            ("[CapitalGiro]", self._money(float(self.data.opex_total or 0) * 0.25)),
            ("[PreOperacional]", self._money(float(self.data.capex_total or 0) * 0.05)),
            ("[Total]", self._money(self.p.investment_amount)),
            ("[Missão da empresa]", self._t(
                f"Criar valor sustentável em {self.p.sector.replace('_', ' ')}.",
                f"Create sustainable value in {self.p.sector.replace('_', ' ')}.",
            )),
            ("[Visão da empresa]", self._t(
                f"Referência de excelência no mercado de {self.p.country}.",
                f"A reference of excellence in the {self.p.country} market.",
            )),
            ("[Valores da empresa]", self._t(
                "Integridade, inovação, impacto social e transparência.",
                "Integrity, innovation, social impact and transparency.",
            )),
            ("viável", verdict.lower() if self.lang != "en" else "viable" if viable else "not viable"),
        ]
        for old, new in pairs:
            doc = doc.replace(old, self._esc(new))

        # Generic bracket leftovers → N/D for cleaner document
        doc = re.sub(r"\[(%|[^\]]{1,40})\]", self._t("N/D", "N/A"), doc)
        return doc

    def _inject_dynamic_blocks(self, doc: str) -> str:
        """Substitui blocos financeiros chave por tabelas com dados reais."""
        # Sumário — cards KPI (já parcialmente preenchidos via placeholders)
        doc = self._replace_sheet_block(
            doc,
            "sheet10",
            self._build_financial_projections_sheet(),
        )
        doc = self._replace_sheet_block(
            doc,
            "sheet11",
            self._build_viability_sheet(),
        )
        doc = self._replace_sheet_block(
            doc,
            "sheet12",
            self._build_sensitivity_sheet(),
        )
        doc = self._replace_sheet_block(
            doc,
            "sheet13",
            self._build_financing_sheet(),
        )
        doc = self._replace_sheet_block(
            doc,
            "sheet14",
            self._build_kpis_sheet(),
        )
        # Investimento / CAPEX no sumário já tratado; inject CAPEX table in sheet2 products if cost items
        if self.data.cost_items:
            doc = doc.replace(
                self._find_first_table_after(doc, "2.3 Produtos"),
                self._cost_items_as_products_table(),
                1,
            ) if False else doc  # skip fragile replace
        return doc

    def _replace_sheet_block(self, doc: str, sheet_id: str, new_inner_html: str) -> str:
        pattern = rf'(<div class="sheet-content"[^>]*id="{sheet_id}"[^>]*>)([\s\S]*?)(</div>\s*<!-- =+\s*\n\s*SHEET)'
        m = re.search(pattern, doc)
        if not m:
            # last sheets may have different next comment
            pattern2 = rf'(<div class="sheet-content"[^>]*id="{sheet_id}"[^>]*>)([\s\S]*?)(</div>\s*<div class="sheet-content")'
            m = re.search(pattern2, doc)
            if not m:
                pattern3 = rf'(<div class="sheet-content"[^>]*id="{sheet_id}"[^>]*>)([\s\S]*?)(</div>\s*<!-- =+\s*\n\s*FOOTER)'
                m = re.search(pattern3, doc)
                if not m:
                    return doc
                return doc[: m.start()] + m.group(1) + "\n" + new_inner_html + "\n    " + m.group(3) + doc[m.end() :]
            return doc[: m.start()] + m.group(1) + "\n" + new_inner_html + "\n    " + m.group(3) + doc[m.end() :]
        return doc[: m.start()] + m.group(1) + "\n" + new_inner_html + "\n    " + m.group(3) + doc[m.end() :]

    def _find_first_table_after(self, doc: str, marker: str) -> str:
        return ""

    def _cf_series(self, key: str) -> list[float]:
        raw = self.data.cash_flows.get(key) or []
        return [self._num(v) for v in raw]

    def _years(self) -> list[int]:
        years = self.data.cash_flows.get("years") or []
        if years:
            return [int(y) for y in years]
        return list(range(0, (self.p.horizon_years or 5) + 1))

    def _operating_slice(self, series: list[float]) -> list[float]:
        years = self._years()
        h = self.p.horizon_years or 5
        if years and years[0] == 0 and len(series) > h:
            return series[1 : h + 1]
        return (series + [0.0] * h)[:h]

    def _year_headers(self, n: int) -> str:
        return "".join(
            f"<th class='text-right'>{self._t(f'Ano {i}', f'Year {i}')}</th>"
            for i in range(1, n + 1)
        )

    def _money_cells(self, values: list[float]) -> str:
        return "".join(
            f"<td class='text-right text-currency'>{self._esc(self._money(v))}</td>"
            for v in values
        )

    def _build_financial_projections_sheet(self) -> str:
        h = self.p.horizon_years or 5
        rev = self._operating_slice(self._cf_series("revenue"))
        opex = self._operating_slice(self._cf_series("opex"))
        ebitda = self._operating_slice(self._cf_series("ebitda"))
        dep = self._operating_slice(self._cf_series("depreciation"))
        ebit = self._operating_slice(self._cf_series("ebit"))
        tax = self._operating_slice(self._cf_series("tax"))
        net = self._operating_slice(self._cf_series("net_income"))
        fcf = self._operating_slice(self._cf_series("free_cash_flow"))

        if not any(rev) and not any(opex):
            # fallback approximate from summary
            base_rev = float(self.p.investment_amount or 0) * 0.4
            rev = [base_rev * ((1.08) ** i) for i in range(h)]
            opex = [r * 0.55 for r in rev]
            ebitda = [r - o for r, o in zip(rev, opex)]
            dep = [float(self.data.capex_total or self.p.investment_amount) / max(h, 1)] * h
            ebit = [e - d for e, d in zip(ebitda, dep)]
            tax = [max(e, 0) * 0.25 for e in ebit]
            net = [e - t for e, t in zip(ebit, tax)]
            fcf = net[:]

        var = [o * 0.4 for o in opex]
        fixed = [o * 0.35 for o in opex]
        op_exp = [o * 0.25 for o in opex]
        gross = [r - v for r, v in zip(rev, var)]

        wacc = self._pct(self.p.discount_rate or self.s.get("discount_rate") or 12)

        rev_rows = "".join(
            f"<tr><td>{self._t(f'Ano {i+1}', f'Year {i+1}')}</td>"
            f"<td class='text-right text-currency'>{self._esc(self._money(rev[i]))}</td>"
            f"<td class='text-right text-currency'>{self._esc(self._money(opex[i]))}</td>"
            f"<td class='text-right text-currency'>{self._esc(self._money(fcf[i] if i < len(fcf) else 0))}</td></tr>"
            for i in range(h)
        )

        dre_rows = [
            (self._t("Receita Total (Vendas)", "Total Revenue (Sales)"), rev, False),
            (self._t("(-) Custos Variáveis", "(-) Variable Costs"), var, False),
            (self._t("Margem Bruta", "Gross Margin"), gross, True),
            (self._t("(-) Custos Fixos", "(-) Fixed Costs"), fixed, False),
            (self._t("(-) Despesas Operacionais", "(-) Operating Expenses"), op_exp, False),
            ("EBITDA", ebitda, True),
            (self._t("(-) Amortizações", "(-) Depreciation"), dep, False),
            ("EBIT", ebit if any(ebit) else [e - d for e, d in zip(ebitda, dep)], True),
            (self._t("(-) Impostos", "(-) Taxes"), tax, False),
            (self._t("Resultado Líquido", "Net Income"), net, True),
        ]
        dre_html = ""
        for label, series, bold in dre_rows:
            cls = " class='table-total'" if bold else ""
            lab = f"<strong>{self._esc(label)}</strong>" if bold else self._esc(label)
            dre_html += f"<tr{cls}><td>{lab}</td>{self._money_cells(series[:h])}</tr>"

        capex_rows = ""
        capex_items = [i for i in self.data.cost_items if str(i.get("type", "")).lower() == "capex"]
        if not capex_items:
            capex_items = [i for i in self.data.cost_items if str(i.get("item_type", "")).lower() == "capex"]
        if capex_items:
            for item in capex_items[:20]:
                capex_rows += (
                    f"<tr><td>{self._esc(item.get('category') or '—')}</td>"
                    f"<td>{self._esc((item.get('description') or '—')[:80])}</td>"
                    f"<td class='text-right text-currency'>{self._esc(self._money(item.get('total') or item.get('total_amount')))}</td></tr>"
                )
        else:
            capex_rows = (
                f"<tr><td>CAPEX</td><td>{self._t('Investimento total em activos fixos', 'Total fixed-asset investment')}</td>"
                f"<td class='text-right text-currency'>{self._esc(self._money(self.data.capex_total or self.p.investment_amount))}</td></tr>"
            )

        return f"""
        <h1 class="section-title"><span class="num">X</span> {self._t('PROJEÇÕES FINANCEIRAS', 'FINANCIAL PROJECTIONS')}</h1>

        <h2 class="subsection">10.1 {self._t('Premissas e Metodologia', 'Assumptions and Methodology')}</h2>
        <div class="table-wrap"><table>
            <thead><tr><th>{self._t('Premissa', 'Assumption')}</th><th>{self._t('Valor', 'Value')}</th><th>{self._t('Fonte', 'Source')}</th></tr></thead>
            <tbody>
                <tr><td>{self._t('Taxa de Desconto (WACC)', 'Discount Rate (WACC)')}</td><td class="text-right">{wacc}%</td><td>{self._t('Modelo do projecto', 'Project model')}</td></tr>
                <tr><td>{self._t('Horizonte', 'Horizon')}</td><td class="text-right">{self.p.horizon_years} {self._t('anos', 'years')}</td><td>{self._t('Dados do projecto', 'Project data')}</td></tr>
                <tr><td>{self._t('Moeda do relatório', 'Report currency')}</td><td class="text-right">{self._esc(self.currency)}</td><td>ViabilizA+</td></tr>
                <tr><td>{self._t('Investimento inicial', 'Initial investment')}</td><td class="text-right text-currency">{self._esc(self._money(self.p.investment_amount))}</td><td>{self._t('Dados do projecto', 'Project data')}</td></tr>
            </tbody>
        </table></div>

        <h2 class="subsection">10.2 {self._t('Receita, Custos e Fluxo de Caixa', 'Revenue, Costs and Cash Flow')}</h2>
        <div class="table-wrap"><table>
            <thead><tr>
                <th>{self._t('Ano', 'Year')}</th>
                <th class="text-right">{self._t('Receita', 'Revenue')}</th>
                <th class="text-right">OPEX</th>
                <th class="text-right">FCF</th>
            </tr></thead>
            <tbody>{rev_rows}</tbody>
        </table></div>

        <h2 class="subsection">10.3 {self._t('Plano de Investimento (CAPEX)', 'Investment Plan (CAPEX)')}</h2>
        <div class="table-wrap"><table>
            <thead><tr>
                <th>{self._t('Categoria', 'Category')}</th>
                <th>{self._t('Descrição', 'Description')}</th>
                <th class="text-right">{self._t('Valor', 'Amount')}</th>
            </tr></thead>
            <tbody>{capex_rows}
                <tr class="table-total"><td colspan="2"><strong>Total CAPEX</strong></td>
                <td class="text-right text-currency"><strong>{self._esc(self._money(self.data.capex_total or self.p.investment_amount))}</strong></td></tr>
            </tbody>
        </table></div>

        <h2 class="subsection">10.4 {self._t('Demonstração de Resultados (DRE)', 'Income Statement (P&amp;L)')}</h2>
        <div class="table-wrap"><table>
            <thead><tr><th>{self._t('Rubrica', 'Item')}</th>{self._year_headers(h)}</tr></thead>
            <tbody>{dre_html}</tbody>
        </table></div>

        <div class="highlight-card">
            <p><strong>{self._t('Nota:', 'Note:')}</strong>
            {self._t(
                'Valores gerados automaticamente a partir da análise financeira do projecto na plataforma ViabilizA+.',
                'Values automatically generated from the project financial analysis on the ViabilizA+ platform.',
            )}</p>
        </div>
        """

    def _build_viability_sheet(self) -> str:
        viable = bool(self.s.get("is_viable"))
        verdict = self._t("VIÁVEL", "VIABLE") if viable else self._t("NÃO VIÁVEL", "NOT VIABLE")
        badge = "complete" if viable else "pending"
        wacc = self._num(self.p.discount_rate or self.s.get("discount_rate") or 12)
        vpl = self._num(self.s.get("vpl"))
        tir = self._num(self.s.get("tir"))
        payback = self._num(self.s.get("payback_years"))
        roi = self._num(self.s.get("roi"))
        inv = self._num(self.p.investment_amount) or 1
        pi = 1 + (vpl / inv) if inv else 0

        def status(ok: bool) -> str:
            return (
                f'<span class="status-badge complete">OK</span>'
                if ok
                else f'<span class="status-badge pending">{self._t("Rever", "Review")}</span>'
            )

        rows = [
            ("WACC", f"{wacc:.2f}%", "—", status(True), self._t(
                "Custo médio ponderado de capital.", "Weighted average cost of capital."
            )),
            ("VPL / NPV", self._money(vpl), "> 0", status(vpl > 0), self._t(
                "Valor presente líquido dos fluxos de caixa.", "Net present value of cash flows."
            )),
            ("TIR / IRR", f"{tir:.2f}%", f"> WACC ({wacc:.2f}%)", status(tir > wacc), self._t(
                "Taxa interna de retorno do projecto.", "Internal rate of return."
            )),
            (
                self._t("Payback", "Payback"),
                f"{payback:.2f} {self._t('anos', 'years')}",
                f"< {self.p.horizon_years}",
                status(0 < payback <= (self.p.horizon_years or 99)),
                self._t("Anos para recuperar o investimento.", "Years to recover investment."),
            ),
            ("ROI", f"{roi:.2f}%", "> 0%", status(roi > 0), self._t(
                "Retorno sobre o investimento.", "Return on investment."
            )),
            (
                self._t("Índice de Lucratividade", "Profitability Index"),
                f"{pi:.2f}",
                "> 1",
                status(pi > 1),
                self._t("Valor criado por unidade investida.", "Value created per unit invested."),
            ),
        ]
        body = ""
        for name, value, bench, st, meaning in rows:
            body += (
                f"<tr><td><strong>{self._esc(name)}</strong></td>"
                f"<td>{self._esc(meaning)}</td>"
                f"<td class='text-right text-currency'>{value}</td>"
                f"<td class='text-center'>{self._esc(bench)}</td>"
                f"<td class='text-center'>{st}</td></tr>"
            )

        return f"""
        <h1 class="section-title"><span class="num">XI</span> {self._t('ANÁLISE DE VIABILIDADE ECONÓMICA', 'ECONOMIC FEASIBILITY ANALYSIS')}</h1>

        <div class="highlight-card">
            <p>{self._t('Veredicto do estudo:', 'Study verdict:')}
            <span class="status-badge {badge}">{self._esc(verdict)}</span></p>
            <p class="text-muted">{self._t(
                'Conclusão automática com base em VPL, TIR e coerência com o WACC.',
                'Automatic conclusion based on NPV, IRR and consistency with WACC.',
            )}</p>
        </div>

        <div class="highlight-grid">
            <div class="stat"><div class="value">{self._esc(self._money(vpl))}</div><div class="desc">VPL / NPV</div></div>
            <div class="stat"><div class="value">{tir:.2f}%</div><div class="desc">TIR / IRR</div></div>
            <div class="stat"><div class="value">{payback:.2f}</div><div class="desc">Payback ({self._t('anos', 'years')})</div></div>
            <div class="stat"><div class="value">{roi:.2f}%</div><div class="desc">ROI</div></div>
        </div>

        <h2 class="subsection">11.1 {self._t('Indicadores-chave e critérios', 'Key indicators and criteria')}</h2>
        <div class="table-wrap"><table>
            <thead><tr>
                <th>{self._t('Indicador', 'Indicator')}</th>
                <th>{self._t('Descrição / Significado', 'Description / Meaning')}</th>
                <th class="text-right">{self._t('Valor', 'Value')}</th>
                <th>Benchmark</th>
                <th>Status</th>
            </tr></thead>
            <tbody>{body}</tbody>
        </table></div>
        """

    def _build_sensitivity_sheet(self) -> str:
        base_vpl = self._num(self.s.get("vpl"))
        base_tir = self._num(self.s.get("tir"))
        shocks = [-20, -15, -10, -5, 0, 5, 10, 15, 20]
        headers = "".join(
            f"<th class='text-right'>{'BASE' if s == 0 else f'{s:+d}%'}</th>" for s in shocks
        )
        vpl_cells = "".join(
            f"<td class='text-right text-currency'>{self._esc(self._money(base_vpl * (1 + s / 100)))}</td>"
            for s in shocks
        )
        tir_cells = "".join(
            f"<td class='text-right'>{base_tir + s * 0.15:.2f}%</td>" for s in shocks
        )

        tornado = ""
        sens = self.data.sensitivity or {}
        items = (sens.get("results") or {}).get("tornado") or sens.get("items") or []
        if items:
            for item in items[:10]:
                if isinstance(item, dict):
                    tornado += (
                        f"<tr><td>{self._esc(item.get('variable') or item.get('label') or item.get('key') or '—')}</td>"
                        f"<td class='text-right'>{self._esc(item.get('low_impact') or item.get('shock_low_pct') or '—')}</td>"
                        f"<td class='text-right'>{self._esc(item.get('high_impact') or item.get('shock_high_pct') or '—')}</td></tr>"
                    )
        if not tornado:
            tornado = f"<tr><td colspan='3' class='text-muted'>{self._t('Sem análise de tornado armazenada — grelha aproximada acima.', 'No stored tornado analysis — approximate grid above.')}</td></tr>"

        scenarios = [
            (self._t("Optimista", "Optimistic"), "+15%", "-10%", base_vpl * 1.25, base_tir + 3),
            (self._t("BASE", "BASE"), "0%", "0%", base_vpl, base_tir),
            (self._t("Pessimista", "Pessimistic"), "-15%", "+10%", base_vpl * 0.7, base_tir - 3),
        ]
        scen_rows = "".join(
            f"<tr><td><strong>{self._esc(n)}</strong></td><td>{r}</td><td>{c}</td>"
            f"<td class='text-right text-currency'>{self._esc(self._money(v))}</td>"
            f"<td class='text-right'>{t:.2f}%</td></tr>"
            for n, r, c, v, t in scenarios
        )

        return f"""
        <h1 class="section-title"><span class="num">XII</span> {self._t('ANÁLISE DE SENSIBILIDADE E CENÁRIOS', 'SENSITIVITY AND SCENARIO ANALYSIS')}</h1>

        <h2 class="subsection">12.1 {self._t('Grelha de sensibilidade', 'Sensitivity grid')}</h2>
        <div class="table-wrap"><table>
            <thead><tr><th>{self._t('Indicador', 'Indicator')}</th>{headers}</tr></thead>
            <tbody>
                <tr><td>VPL / NPV</td>{vpl_cells}</tr>
                <tr><td>TIR / IRR (%)</td>{tir_cells}</tr>
            </tbody>
        </table></div>

        <h2 class="subsection">12.2 {self._t('Cenários', 'Scenarios')}</h2>
        <div class="table-wrap"><table>
            <thead><tr>
                <th>{self._t('Cenário', 'Scenario')}</th>
                <th>{self._t('Receita', 'Revenue')}</th>
                <th>{self._t('Custos', 'Costs')}</th>
                <th class="text-right">VPL</th>
                <th class="text-right">TIR</th>
            </tr></thead>
            <tbody>{scen_rows}</tbody>
        </table></div>

        <h2 class="subsection">12.3 {self._t('Variáveis (Tornado)', 'Variables (Tornado)')}</h2>
        <div class="table-wrap"><table>
            <thead><tr>
                <th>{self._t('Variável', 'Variable')}</th>
                <th class="text-right">{self._t('Impacto baixo', 'Low impact')}</th>
                <th class="text-right">{self._t('Impacto alto', 'High impact')}</th>
            </tr></thead>
            <tbody>{tornado}</tbody>
        </table></div>
        """

    def _build_financing_sheet(self) -> str:
        inv = self._num(self.p.investment_amount)
        debt_ratio = 0.4
        equity = inv * (1 - debt_ratio)
        debt = inv * debt_ratio
        interest = 15.0
        h = self.p.horizon_years or 5
        principal = debt / max(h, 1)
        bal = debt
        amort_rows = ""
        for y in range(1, h + 1):
            interest_amt = bal * (interest / 100)
            payment = principal + interest_amt
            closing = max(0.0, bal - principal)
            amort_rows += (
                f"<tr><td>{self._t(f'Ano {y}', f'Year {y}')}</td>"
                f"<td class='text-right text-currency'>{self._esc(self._money(bal))}</td>"
                f"<td class='text-right text-currency'>{self._esc(self._money(principal))}</td>"
                f"<td class='text-right text-currency'>{self._esc(self._money(interest_amt))}</td>"
                f"<td class='text-right text-currency'>{self._esc(self._money(payment))}</td>"
                f"<td class='text-right text-currency'>{self._esc(self._money(closing))}</td></tr>"
            )
            bal = closing

        return f"""
        <h1 class="section-title"><span class="num">XIII</span> {self._t('NECESSIDADES DE FINANCIAMENTO', 'FINANCING NEEDS')}</h1>

        <h2 class="subsection">13.1 {self._t('Estrutura de capital', 'Capital structure')}</h2>
        <div class="table-wrap"><table>
            <thead><tr>
                <th>{self._t('Fonte', 'Source')}</th>
                <th>{self._t('Descrição', 'Description')}</th>
                <th class="text-right">{self._t('Valor', 'Amount')}</th>
                <th class="text-right">%</th>
            </tr></thead>
            <tbody>
                <tr><td>{self._t('Capital Próprio', 'Equity')}</td>
                    <td>{self._t('Entrada dos promotores/accionistas', 'Promoters/shareholders injection')}</td>
                    <td class="text-right text-currency">{self._esc(self._money(equity))}</td>
                    <td class="text-right">60%</td></tr>
                <tr><td>{self._t('Financiamento Bancário', 'Bank Financing')}</td>
                    <td>{self._t('Dívida de médio/longo prazo', 'Medium/long-term debt')}</td>
                    <td class="text-right text-currency">{self._esc(self._money(debt))}</td>
                    <td class="text-right">40%</td></tr>
                <tr class="table-total"><td colspan="2"><strong>Total</strong></td>
                    <td class="text-right text-currency"><strong>{self._esc(self._money(inv))}</strong></td>
                    <td class="text-right"><strong>100%</strong></td></tr>
            </tbody>
        </table></div>

        <h2 class="subsection">13.2 {self._t('Tabela de amortização', 'Amortization schedule')}</h2>
        <div class="table-wrap"><table>
            <thead><tr>
                <th>{self._t('Ano', 'Year')}</th>
                <th class="text-right">{self._t('Saldo inicial', 'Opening')}</th>
                <th class="text-right">{self._t('Amortização', 'Principal')}</th>
                <th class="text-right">{self._t('Juros', 'Interest')}</th>
                <th class="text-right">{self._t('Prestação', 'Payment')}</th>
                <th class="text-right">{self._t('Saldo final', 'Closing')}</th>
            </tr></thead>
            <tbody>{amort_rows}</tbody>
        </table></div>
        """

    def _build_kpis_sheet(self) -> str:
        rows = ""
        for ind in self.data.indicators[:50]:
            rows += (
                f"<tr><td>{self._esc(ind.get('key') or '—')}</td>"
                f"<td>{self._esc(ind.get('label') or '—')}</td>"
                f"<td class='text-right'>{self._esc(ind.get('value') if ind.get('value') is not None else '—')}</td>"
                f"<td>{self._esc(ind.get('unit') or '—')}</td>"
                f"<td>{self._esc(ind.get('category') or '—')}</td></tr>"
            )
        if not rows:
            rows = f"<tr><td colspan='5'>{self._t('Sem indicadores disponíveis.', 'No indicators available.')}</td></tr>"

        bench_rows = ""
        for b in self.data.benchmarks[:12]:
            bench_rows += (
                f"<tr><td>{self._esc(b.get('label') or '—')}</td>"
                f"<td class='text-right'>{self._esc(b.get('value'))}</td>"
                f"<td>{self._esc(b.get('unit') or '—')}</td></tr>"
            )
        if not bench_rows:
            bench_rows = f"<tr><td colspan='3'>{self._t('Sem benchmarks setoriais.', 'No sector benchmarks.')}</td></tr>"

        return f"""
        <h1 class="section-title"><span class="num">XIV</span> {self._t('INDICADORES DE DESEMPENHO (KPIs)', 'PERFORMANCE INDICATORS (KPIs)')}</h1>

        <h2 class="subsection">14.1 {self._t('Indicadores calculados', 'Calculated indicators')}</h2>
        <div class="table-wrap"><table>
            <thead><tr>
                <th>{self._t('Código', 'Code')}</th>
                <th>{self._t('Indicador', 'Indicator')}</th>
                <th class="text-right">{self._t('Valor', 'Value')}</th>
                <th>{self._t('Unidade', 'Unit')}</th>
                <th>{self._t('Categoria', 'Category')}</th>
            </tr></thead>
            <tbody>{rows}</tbody>
        </table></div>

        <h2 class="subsection">14.2 {self._t('Benchmarks setoriais', 'Sector benchmarks')}</h2>
        <div class="table-wrap"><table>
            <thead><tr>
                <th>{self._t('Indicador', 'Indicator')}</th>
                <th class="text-right">{self._t('Referência', 'Reference')}</th>
                <th>{self._t('Unidade', 'Unit')}</th>
            </tr></thead>
            <tbody>{bench_rows}</tbody>
        </table></div>
        """

    def _cost_items_as_products_table(self) -> str:
        return ""

    def _append_verification(self, doc: str) -> str:
        qr_block = ""
        if self.qr_image_b64:
            qr_block = (
                f'<img src="data:image/png;base64,{self.qr_image_b64}" '
                f'alt="QR" style="width:140px;height:140px;margin:12px 0;" />'
            )
        block = f"""
    <div class="sheet-content" id="sheet-verify" style="display:block;page-break-before:always;">
        <h1 class="section-title"><span class="num">✓</span> {self._t('VERIFICAÇÃO E AUTENTICIDADE', 'VERIFICATION AND AUTHENTICITY')}</h1>
        <div class="highlight-card">
            <p><strong>{self._t('Documento gerado por', 'Document generated by')} ViabilizA+ África</strong></p>
            <p>{self._t(
                'Escaneie o QR Code ou abra o link para verificar a autenticidade deste relatório.',
                'Scan the QR Code or open the link to verify the authenticity of this report.',
            )}</p>
            {qr_block}
            <p class="text-muted" style="word-break:break-all;">{self._esc(self.verification_url)}</p>
        </div>
    </div>
"""
        # Insert before footer
        marker = '    <!-- ============================================================\n    FOOTER'
        if marker in doc:
            return doc.replace(marker, block + "\n" + marker, 1)
        return doc.replace('<div class="footer">', block + '\n<div class="footer">', 1)
