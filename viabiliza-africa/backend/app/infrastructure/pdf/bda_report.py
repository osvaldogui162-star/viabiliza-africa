from reportlab.platypus import PageBreak, Paragraph, Spacer

from app.infrastructure.pdf.pdf_base import PdfReportBuilder


class BdaReportPdf(PdfReportBuilder):
    """UC30 — Formulário BDA com tabela de reembolsos automática."""

    def _sections(self) -> list[str]:
        return [
            self._t("Capa e identificação do requerente", "Cover and applicant identification"),
            self._t("Dados gerais do projecto", "General project data"),
            self._t("Objectivos e justificação", "Objectives and justification"),
            self._t("Mercado e concorrência", "Market and competition"),
            self._t("Localização e infraestruturas", "Location and infrastructure"),
            self._t("Tecnologia e processos", "Technology and processes"),
            self._t("Recursos humanos", "Human resources"),
            self._t("Plano de investimento fixo (CAPEX)", "Fixed investment plan (CAPEX)"),
            self._t("Necessidades de fundo de maneio (OPEX)", "Working capital needs (OPEX)"),
            self._t("Cronograma de execução", "Execution schedule"),
            self._t("Fontes de financiamento", "Funding sources"),
            self._t("Estrutura accionista", "Shareholder structure"),
            self._t("Garantias propostas", "Proposed guarantees"),
            self._t("Projeções de vendas", "Sales projections"),
            self._t("Custos operacionais", "Operating costs"),
            self._t("Resultados operacionais", "Operating results"),
            self._t("Fluxo de caixa projectado", "Projected cash flow"),
            self._t("Balanço projectado", "Projected balance sheet"),
            self._t("Indicadores de rentabilidade", "Profitability indicators"),
            self._t("Análise de sensibilidade", "Sensitivity analysis"),
            self._t("Impacto social e ambiental", "Social and environmental impact"),
            self._t("Tabela de reembolso do empréstimo", "Loan repayment schedule"),
            self._t("Declaração e anexos", "Declaration and annexes"),
        ]

    def build(self) -> bytes:
        p = self.data.project
        s = self.data.indicators_summary
        rate = float(p.discount_rate or 12) / 100
        principal = float(p.investment_amount) * self.data.exchange_rate
        years = p.horizon_years or 5
        annual_payment = self._amortization(principal, rate, years)
        sections = self._sections()
        tbd = self._t("N/D", "N/A")

        self.add_cover(
            self._t("FORMULÁRIO BDA", "BDA FORM"),
            self._t("Banco de Desenvolvimento de Angola", "Banco de Desenvolvimento de Angola"),
            self._t(
                "Estudo de Viabilidade — Formulário Institucional",
                "Feasibility Study — Institutional Form",
            ),
        )

        self.elements.append(
            Paragraph(
                self._t(
                    "Índice do Formulário BDA (Estrutura Institucional)",
                    "BDA Form Index (Institutional Structure)",
                ),
                self.styles["SectionHeader"],
            )
        )
        index_rows = []
        for i in range(1, 62):
            section_idx = min((i - 1) // 3, len(sections) - 1)
            index_rows.append([
                str(i),
                sections[section_idx],
                self._t(f"Secção {section_idx + 1}", f"Section {section_idx + 1}"),
            ])
        self.add_table(
            [
                self._t("Pág.", "Page"),
                self._t("Conteúdo", "Content"),
                self._t("Grupo", "Group"),
            ],
            index_rows[:30],
        )
        self.elements.append(PageBreak())
        self.add_table(
            [
                self._t("Pág.", "Page"),
                self._t("Conteúdo", "Content"),
                self._t("Grupo", "Group"),
            ],
            index_rows[30:],
        )

        for idx, section in enumerate(sections, 1):
            body = self._section_body(idx, section, s, tbd)
            self.add_section(idx, section, body)

        self.add_section(
            len(sections) + 1,
            self._t("Tabela de Reembolso Automática", "Automatic Repayment Schedule"),
            self._t(
                f"Empréstimo: {self._money(principal)}. Taxa: {rate * 100:.2f}%. "
                f"Prazo: {years} anos. Prestação anual: {self._money(annual_payment)}.",
                f"Loan: {self._money(principal)}. Rate: {rate * 100:.2f}%. "
                f"Term: {years} years. Annual payment: {self._money(annual_payment)}.",
            ),
        )
        rows = self._reimbursement_table(principal, rate, years)
        self.add_table(
            [
                self._t("Ano", "Year"),
                self._t("Prestação", "Payment"),
                self._t("Juros", "Interest"),
                self._t("Amortização", "Amortization"),
                self._t("Saldo", "Balance"),
            ],
            rows,
        )

        self.add_qr_verification_page()
        return self.build_pdf()

    def _section_body(self, idx: int, section: str, summary: dict, tbd: str) -> str:
        p = self.data.project
        capex_label = self._t("CAPEX", "CAPEX")
        opex_label = self._t("OPEX", "OPEX")
        if capex_label in section or "CAPEX" in section:
            return self._t(
                f"Total CAPEX: {self._money(self.data.capex_total)}. Itens: {len(self.data.cost_items)}.",
                f"Total CAPEX: {self._money(self.data.capex_total)}. Items: {len(self.data.cost_items)}.",
            )
        if opex_label in section or "OPEX" in section:
            return self._t(
                f"Total OPEX: {self._money(self.data.opex_total)}.",
                f"Total OPEX: {self._money(self.data.opex_total)}.",
            )
        indicators_pt = self._t("Indicadores", "Indicators")
        if indicators_pt in section or "Indicators" in section or "rentabilidade" in section.lower():
            return self._t(
                f"VPL: {self._money(summary.get('vpl', 0))}. TIR: {summary.get('tir', tbd)}%. "
                f"ROI: {summary.get('roi', tbd)}%.",
                f"NPV: {self._money(summary.get('vpl', 0))}. IRR: {summary.get('tir', tbd)}%. "
                f"ROI: {summary.get('roi', tbd)}%.",
            )
        if "reembolso" in section.lower() or "repayment" in section.lower():
            return self._t(
                "Ver tabela de amortização automática na secção final.",
                "See automatic amortization table in the final section.",
            )
        return self._t(
            f"Dados do projecto «{p.name}» — {p.company_name}. "
            f"País: {p.country}. Investimento: {self._money(p.investment_amount)}.",
            f"Project data «{p.name}» — {p.company_name}. "
            f"Country: {p.country}. Investment: {self._money(p.investment_amount)}.",
        )

    @staticmethod
    def _amortization(principal: float, rate: float, years: int) -> float:
        if rate <= 0 or years <= 0:
            return principal / max(years, 1)
        return principal * (rate * (1 + rate) ** years) / ((1 + rate) ** years - 1)

    def _reimbursement_table(self, principal: float, rate: float, years: int) -> list[list]:
        payment = self._amortization(principal, rate, years)
        balance = principal
        rows = []
        for year in range(1, years + 1):
            interest = balance * rate
            amort = payment - interest
            balance = max(0, balance - amort)
            rows.append(
                [
                    str(year),
                    self._money(payment),
                    self._money(interest),
                    self._money(amort),
                    self._money(balance),
                ]
            )
        return rows
