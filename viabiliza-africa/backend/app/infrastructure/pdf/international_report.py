from app.infrastructure.pdf.general_report_html import GeneralReportHtmlBuilder
from app.infrastructure.pdf.pdf_base import PdfReportBuilder


class InternationalReportPdf(PdfReportBuilder):
    """UC28 — Relatório Geral (modelo HTML institucional com 23 secções).

    Segue o «RELATÓRIO MODELO GERAL DO ViabilizA+»: índice, sumário, negócio,
    mercado, SWOT, financeiro, viabilidade, KPIs, ESG, etc. O PDF é gerado
    a partir do HTML preenchido (Chrome/Edge). Se o browser falhar, usa o
    fallback ReportLab resumido.
    """

    def build(self) -> bytes:
        try:
            return GeneralReportHtmlBuilder(
                self.data,
                verification_url=self.verification_url,
                qr_image_b64=self.qr_image_b64,
            ).build_pdf()
        except Exception:
            return self._build_fallback_pdf()

    def _build_fallback_pdf(self) -> bytes:
        """Fallback ReportLab se Chrome/Edge não estiver disponível."""
        p = self.data.project
        s = self.data.indicators_summary

        self.add_cover(
            self._t("RELATÓRIO DE VIABILIDADE", "FEASIBILITY REPORT"),
            self._t("Modelo Geral Internacional", "International General Model"),
            "IFC / OECD Investment Guidelines · ViabilizA+ Modelo Geral",
        )

        viable = s.get("is_viable", False)
        self.add_section(
            1,
            self._t("I. Sumário Executivo", "I. Executive Summary"),
            self._t(
                f"O presente estudo avalia a viabilidade do projecto «{p.name}» promovido por "
                f"{p.company_name}, com investimento de {self._money(p.investment_amount)} "
                f"e horizonte de {p.horizon_years} anos. "
                f"Conclusão: {'VIÁVEL' if viable else 'REQUER ANÁLISE ADICIONAL'}. "
                f"VPL: {self._money(s.get('vpl', 0))}, TIR: {s.get('tir', 'N/A')}%, "
                f"Payback: {s.get('payback_years', 'N/A')} anos.",
                f"This study assesses the feasibility of project «{p.name}» by {p.company_name}, "
                f"with investment of {self._money(p.investment_amount)} over {p.horizon_years} years. "
                f"Conclusion: {'VIABLE' if viable else 'REQUIRES FURTHER ANALYSIS'}. "
                f"NPV: {self._money(s.get('vpl', 0))}, IRR: {s.get('tir', 'N/A')}%, "
                f"Payback: {s.get('payback_years', 'N/A')} years.",
            ),
        )

        self.add_section(
            2,
            self._t("II. Identificação do Projecto", "II. Project Identification"),
            self._t(
                f"Empresa: {p.company_name}. NIF: {p.company_tax_id or 'N/D'}. "
                f"País: {p.country}. Sector: {p.sector}. "
                f"Estado: {p.status}. Responsável: {p.owner_name or 'N/D'}.",
                f"Company: {p.company_name}. Tax ID: {p.company_tax_id or 'N/A'}. "
                f"Country: {p.country}. Sector: {p.sector}. "
                f"Status: {p.status}. Owner: {p.owner_name or 'N/A'}.",
            ),
        )

        self.add_section(
            3,
            self._t("III. Descrição e Objectivos", "III. Description and Objectives"),
            p.description
            or self._t(
                "Projecto de investimento com foco no mercado africano.",
                "Investment project focused on the African market.",
            ),
        )

        bench_rows = [
            [b["label"], str(b["value"]), b["unit"]] for b in self.data.benchmarks[:8]
        ]
        if bench_rows:
            self.add_section(
                4,
                self._t("IV. Análise de Mercado e Benchmarks", "IV. Market Analysis and Benchmarks"),
                self._t(
                    "Comparação com médias setoriais do mercado africano.",
                    "Comparison with African sector averages.",
                ),
            )
            self.add_table(
                [
                    self._t("Indicador", "Indicator"),
                    self._t("Média Setorial", "Sector Average"),
                    self._t("Unidade", "Unit"),
                ],
                bench_rows,
            )

        self.add_section(
            5,
            self._t("V. Plano de Investimento", "V. Investment Plan"),
            self._t(
                f"CAPEX total: {self._money(self.data.capex_total)}. "
                f"OPEX anual estimado: {self._money(self.data.opex_total)}.",
                f"Total CAPEX: {self._money(self.data.capex_total)}. "
                f"Estimated annual OPEX: {self._money(self.data.opex_total)}.",
            ),
        )
        if self.data.cost_items:
            rows = [
                [
                    str(i.get("type") or i.get("item_type") or "").upper(),
                    i.get("category") or "—",
                    (i.get("description") or "—")[:40],
                    self._money(i.get("total") or i.get("total_amount") or 0),
                ]
                for i in self.data.cost_items[:25]
            ]
            self.add_table(
                [
                    self._t("Tipo", "Type"),
                    self._t("Categoria", "Category"),
                    self._t("Descrição", "Description"),
                    self._t("Total", "Total"),
                ],
                rows,
            )

        cf = self.data.cash_flows
        if cf.get("years"):
            rows = []
            for idx, year in enumerate(cf["years"]):
                rev = cf["revenue"][idx] if idx < len(cf.get("revenue") or []) else 0
                fcf = cf["free_cash_flow"][idx] if idx < len(cf.get("free_cash_flow") or []) else 0
                rows.append([str(year), self._money(rev), self._money(fcf)])
            self.add_section(
                6,
                self._t("VI. Projeções Financeiras", "VI. Financial Projections"),
                self._t("Fluxos de caixa projectados.", "Projected cash flows."),
            )
            self.add_table(
                [
                    self._t("Ano", "Year"),
                    self._t("Receita", "Revenue"),
                    self._t("FCF", "FCF"),
                ],
                rows,
            )

        if self.data.indicators:
            rows = [
                [
                    ind.get("label", "—"),
                    str(ind["value"]) if ind.get("value") is not None else "—",
                    ind.get("unit", "—"),
                ]
                for ind in self.data.indicators[:40]
            ]
            self.add_section(
                7,
                self._t("VII. Indicadores de Viabilidade", "VII. Feasibility Indicators"),
                self._t(
                    f"Total de {len(self.data.indicators)} indicadores calculados automaticamente.",
                    f"Total of {len(self.data.indicators)} automatically calculated indicators.",
                ),
            )
            self.add_table(
                [
                    self._t("Indicador", "Indicator"),
                    self._t("Valor", "Value"),
                    self._t("Unidade", "Unit"),
                ],
                rows,
            )

        risk_pt = (
            f"Tarefas concluídas: {self.data.tasks_summary.get('done', 0)} de "
            f"{self.data.tasks_summary.get('total', 0)}. "
            f"Registos de auditoria: {self.data.audit_trail_count}."
        )
        risk_en = (
            f"Completed tasks: {self.data.tasks_summary.get('done', 0)} of "
            f"{self.data.tasks_summary.get('total', 0)}. "
            f"Audit records: {self.data.audit_trail_count}."
        )
        if self.data.monte_carlo:
            mc = self.data.monte_carlo.get("results", {})
            prob = mc.get("probability_viable") or mc.get("success_probability")
            if prob is not None:
                risk_pt += (
                    f" Monte Carlo ({self.data.monte_carlo['iterations']} iterações): "
                    f"probabilidade de viabilidade {prob:.1%}."
                )
                risk_en += (
                    f" Monte Carlo ({self.data.monte_carlo['iterations']} iterations): "
                    f"viability probability {prob:.1%}."
                )
        self.add_section(
            8,
            self._t("VIII. Análise de Risco", "VIII. Risk Analysis"),
            self._t(risk_pt, risk_en),
        )
        if self.data.sensitivity:
            rows = []
            for item in self.data.sensitivity.get("results", {}).get("tornado", [])[:8]:
                rows.append(
                    [
                        item.get("variable", "—"),
                        str(item.get("low_impact", "—")),
                        str(item.get("high_impact", "—")),
                    ]
                )
            if rows:
                self.add_table(
                    [
                        self._t("Variável", "Variable"),
                        self._t("Impacto Baixo", "Low Impact"),
                        self._t("Impacto Alto", "High Impact"),
                    ],
                    rows,
                )

        if self.data.budgets:
            rows = [
                [b["number"], b["title"], self._money(b["total"]), b["status"]]
                for b in self.data.budgets
            ]
            self.add_section(
                9,
                self._t("IX. Orçamentos Rastreáveis", "IX. Traceable Budgets"),
                self._t("Orçamentos com rastreabilidade.", "Budgets with traceability."),
            )
            self.add_table(
                [
                    self._t("Nº", "No."),
                    self._t("Título", "Title"),
                    self._t("Total", "Total"),
                    self._t("Estado", "Status"),
                ],
                rows,
            )

        self.add_section(
            10,
            self._t("X. Conclusões e Recomendações", "X. Conclusions and Recommendations"),
            self._t(
                "Recomenda-se a prossecução do investimento caso os indicadores "
                "permaneçam coerentes com as premissas aprovadas, com monitorização "
                "contínua de riscos e KPIs.",
                "Proceed with the investment if indicators remain consistent with "
                "approved assumptions, with continuous monitoring of risks and KPIs.",
            ),
        )
        self.add_qr_verification_page()
        return self.build_pdf()
