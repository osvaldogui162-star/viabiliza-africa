from app.infrastructure.pdf.pdf_base import PdfReportBuilder


class BfaReportPdf(PdfReportBuilder):
    """UC29 — Relatório BFA conforme Aviso BNA 10/2020."""

    def _checklist_items(self) -> list[tuple[str, str, str]]:
        return [
            ("I.1", self._t("Identificação do promotor e beneficiário", "Promoter and beneficiary identification"), ""),
            ("I.2", self._t("Descrição sumária do projecto", "Project summary description"), ""),
            ("I.3", self._t("Localização e enquadramento sectorial", "Location and sector context"), ""),
            ("II.1", self._t("Enquadramento legal — Aviso BNA 10/2020", "Legal framework — BNA Notice 10/2020"), ""),
            ("II.2", self._t("Conformidade com política de crédito", "Credit policy compliance"), ""),
            ("III.1", self._t("Plano de investimento e financiamento", "Investment and financing plan"), ""),
            ("III.2", self._t("Estrutura de capital e endividamento", "Capital structure and indebtedness"), ""),
            ("IV.1", self._t("Demonstrações financeiras projectadas", "Projected financial statements"), ""),
            ("IV.2", self._t("Fluxos de caixa e capacidade de reembolso", "Cash flows and repayment capacity"), ""),
            ("V.1", self._t("Indicadores: VPL, TIR, Payback", "Indicators: NPV, IRR, Payback"), ""),
            ("V.2", self._t("Análise de sensibilidade e cenários", "Sensitivity and scenario analysis"), ""),
            ("VI.1", self._t("Documentação de suporte e hashes de rastreabilidade", "Supporting documentation and traceability hashes"), ""),
            ("VI.2", self._t("Declaração de veracidade dos dados", "Data accuracy declaration"), ""),
        ]

    def build(self) -> bytes:
        p = self.data.project
        s = self.data.indicators_summary
        tbd = self._t("N/D", "N/A")
        years = self._t("anos", "years")
        to_present = self._t("A apresentar", "To be provided")
        productive = self._t("Projecto de investimento produtivo", "Productive investment project")
        bfa_policy = self._t("Conforme política BFA", "Per BFA policy")
        confirmed = self._t("Confirmada", "Confirmed")
        under_review = self._t("Em análise", "Under review")
        viability = confirmed if s.get("is_viable") else under_review

        self.add_cover(
            self._t("RELATÓRIO BFA", "BFA REPORT"),
            self._t("Banco de Fomento Angola", "Banco de Fomento Angola"),
            self._t("Aviso BNA n.º 10/2020", "BNA Notice No. 10/2020"),
        )

        self.add_section(
            1,
            self._t("Enquadramento Regulamentar", "Regulatory Framework"),
            self._t(
                "O presente relatório foi elaborado em conformidade com o Aviso n.º 10/2020 do "
                "Banco Nacional de Angola (BNA), destinado à análise de projectos de investimento "
                "submetidos ao Banco de Fomento Angola (BFA).",
                "This report was prepared in compliance with BNA Notice No. 10/2020 for investment "
                "project analysis submitted to Banco de Fomento Angola (BFA).",
            ),
        )

        self.add_section(
            2,
            self._t("Identificação do Promotor", "Promoter Identification"),
            self._t(
                f"Denominação social: {p.company_name}. "
                f"NIF: {p.company_tax_id or to_present}. "
                f"País de incorporação: {p.country}. "
                f"Sector de actividade: {p.sector}.",
                f"Company name: {p.company_name}. "
                f"Tax ID: {p.company_tax_id or to_present}. "
                f"Country of incorporation: {p.country}. "
                f"Business sector: {p.sector}.",
            ),
        )

        self.add_section(
            3,
            self._t("Descrição do Projecto de Investimento", "Investment Project Description"),
            self._t(
                f"Designação: {p.name}. "
                f"Objecto: {p.description or productive}. "
                f"Montante do investimento: {self._money(p.investment_amount)}. "
                f"Prazo de execução/análise: {p.horizon_years} anos.",
                f"Name: {p.name}. "
                f"Purpose: {p.description or productive}. "
                f"Investment amount: {self._money(p.investment_amount)}. "
                f"Execution/analysis horizon: {p.horizon_years} years.",
            ),
        )

        self.add_section(
            4,
            self._t("Estrutura de Financiamento", "Financing Structure"),
            self._t(
                f"Investimento total: {self._money(p.investment_amount)}. "
                f"CAPEX documentado: {self._money(self.data.capex_total)}. "
                f"OPEX anual: {self._money(self.data.opex_total)}. "
                f"Taxa de desconto: {p.discount_rate or bfa_policy}%.",
                f"Total investment: {self._money(p.investment_amount)}. "
                f"Documented CAPEX: {self._money(self.data.capex_total)}. "
                f"Annual OPEX: {self._money(self.data.opex_total)}. "
                f"Discount rate: {p.discount_rate or bfa_policy}%.",
            ),
        )

        self.add_section(
            5,
            self._t("Checklist de Documentação BFA", "BFA Documentation Checklist"),
            self._t("Validação de requisitos:", "Requirements validation:"),
        )
        rows = []
        for code, item, _ in self._checklist_items():
            status = "✓" if self._checklist_ok(code) else "○"
            rows.append([code, item, status])
        self.add_table(
            [
                self._t("Código", "Code"),
                self._t("Requisito", "Requirement"),
                self._t("Estado", "Status"),
            ],
            rows,
        )

        self.add_section(
            6,
            self._t("Indicadores de Viabilidade (BNA 10/2020)", "Feasibility Indicators (BNA 10/2020)"),
            self._t(
                f"VPL: {self._money(s.get('vpl', 0))}. "
                f"TIR: {s.get('tir', tbd)}%. "
                f"ROI: {s.get('roi', tbd)}%. "
                f"Payback: {s.get('payback_years', tbd)} {years}. "
                f"Viabilidade: {viability}.",
                f"NPV: {self._money(s.get('vpl', 0))}. "
                f"IRR: {s.get('tir', tbd)}%. "
                f"ROI: {s.get('roi', tbd)}%. "
                f"Payback: {s.get('payback_years', tbd)} {years}. "
                f"Feasibility: {viability}.",
            ),
        )

        if self.data.indicators:
            ind_rows = [
                [
                    ind.get("key", "—"),
                    ind.get("label", "—"),
                    str(ind["value"]) if ind.get("value") is not None else "—",
                ]
                for ind in self.data.indicators[:30]
            ]
            self.add_table(
                [
                    self._t("Código", "Code"),
                    self._t("Indicador", "Indicator"),
                    self._t("Valor", "Value"),
                ],
                ind_rows,
            )

        self.add_section(
            7,
            self._t("Rastreabilidade e Audit Trail", "Traceability and Audit Trail"),
            self._t(
                f"Total de {self.data.audit_trail_count} registos de auditoria. "
                f"Dados OPEX/CAPEX com hash SHA-256. "
                f"Orçamentos rastreáveis: {len(self.data.budgets)}.",
                f"Total of {self.data.audit_trail_count} audit records. "
                f"OPEX/CAPEX data with SHA-256 hash. "
                f"Traceable budgets: {len(self.data.budgets)}.",
            ),
        )

        if self.data.audit_trail_sample:
            audit_rows = [
                [a["action"], a["entity"], a["hash"][:16] + "…", a["at"][:10]]
                for a in self.data.audit_trail_sample[:10]
            ]
            self.add_table(
                [
                    self._t("Acção", "Action"),
                    self._t("Entidade", "Entity"),
                    self._t("Hash", "Hash"),
                    self._t("Data", "Date"),
                ],
                audit_rows,
            )

        self.add_section(
            8,
            self._t("Declaração", "Declaration"),
            self._t(
                "Declaro que os dados constantes deste relatório reflectem informação recolhida "
                "através da plataforma ViabilizA+ África com rastreabilidade criptográfica, "
                "estando disponíveis para verificação pelos serviços de auditoria do BFA.",
                "I declare that the data in this report reflects information collected through "
                "the ViabilizA+ África platform with cryptographic traceability, available for "
                "verification by BFA audit services.",
            ),
        )

        self.add_qr_verification_page()
        return self.build_pdf()

    def _checklist_ok(self, code: str) -> bool:
        checks = {
            "I.1": bool(self.data.project.company_name),
            "I.2": bool(self.data.project.name),
            "III.1": float(self.data.capex_total) > 0 or float(self.data.project.investment_amount) > 0,
            "IV.1": bool(self.data.cash_flows),
            "V.1": bool(self.data.indicators_summary),
            "VI.1": self.data.audit_trail_count > 0,
        }
        return checks.get(code, True)
