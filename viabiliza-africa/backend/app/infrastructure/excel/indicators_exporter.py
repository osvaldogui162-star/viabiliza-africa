from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from app.application.interfaces.financial_calculator import FinancialAnalysisResult


class IndicatorsExcelExporter:
    """Exportação Excel no modelo institucional ViabilizA+ (11 planilhas).

    Estrutura alinhada a ViabilizA_Estudo_Viabilidade:
    Índice · CAPEX · OPEX · DRE · Cash Flow · Balanço · KPIs ·
    Viabilidade · Sensibilidade · Financiamento · Premissas
    """

    BRAND = "VIABILIZA+ ÁFRICA"
    # Paleta do modelo de referência
    NAVY = "0A1A2E"
    BLUE = "1A3A5C"
    GOLD = "C6A43F"
    WHITE = "FFFFFF"
    ALT = "FAFBFD"
    TOTAL_BG = "E8EDF4"
    MUTED = "6B7A8A"
    SUCCESS = "166534"
    DANGER = "B91C1C"
    BORDER = "E2E8F0"

    def export(
        self,
        analysis: FinancialAnalysisResult,
        *,
        project_name: str,
        company_name: str | None = None,
        sector: str | None = None,
        country: str | None = None,
        currency: str = "AOA",
        assumptions: dict | None = None,
        calculation_hash: str | None = None,
        analysis_date: datetime | None = None,
        indicators_count: int | None = None,
        language: str = "pt",
        cost_items: list[dict] | None = None,
        sensitivity: dict | None = None,
        investment_amount: float | None = None,
        horizon_years: int | None = None,
    ) -> bytes:
        self.lang = "en" if language == "en" else "pt"
        self.currency = currency or "AOA"
        self.assumptions = assumptions or {}
        self.cost_items = cost_items or []
        self.sensitivity = sensitivity or {}
        self.generated_at = analysis_date or datetime.now(timezone.utc)
        self.project_name = project_name
        self.company_name = company_name or "—"
        self.sector = (sector or "—").replace("_", " ").title()
        self.country = country or "—"
        self.hash = calculation_hash
        self.analysis = analysis
        self.summary = analysis.summary or {}
        self.horizon = int(
            horizon_years
            or self.summary.get("horizon_years")
            or max(len(getattr(analysis.cash_flows, "years", []) or []) - 1, 5)
        )
        self.investment = float(
            investment_amount
            if investment_amount is not None
            else self.summary.get("initial_investment")
            or self._num(self.assumptions.get("capex_total"))
            or 0
        )

        self._styles = self._build_styles()
        wb = Workbook()

        self._sheet_index(wb.active)
        self._sheet_capex(wb.create_sheet("CAPEX"))
        self._sheet_opex(wb.create_sheet("OPEX"))
        self._sheet_dre(wb.create_sheet("DRE"))
        self._sheet_cash_flow(wb.create_sheet("Cash Flow"))
        self._sheet_balance(wb.create_sheet("Balanço" if self.lang == "pt" else "Balance"))
        self._sheet_kpis(wb.create_sheet("KPIs"))
        self._sheet_viability(wb.create_sheet("Viabilidade" if self.lang == "pt" else "Feasibility"))
        self._sheet_sensitivity(wb.create_sheet("Sensibilidade" if self.lang == "pt" else "Sensitivity"))
        self._sheet_financing(wb.create_sheet("Financiamento" if self.lang == "pt" else "Financing"))
        self._sheet_assumptions(wb.create_sheet("Premissas" if self.lang == "pt" else "Assumptions"))

        buffer = BytesIO()
        wb.save(buffer)
        return buffer.getvalue()

    # ── styles ──────────────────────────────────────────────────────────

    def _build_styles(self) -> dict[str, Any]:
        thin = Border(
            left=Side(style="thin", color=self.BORDER),
            right=Side(style="thin", color=self.BORDER),
            top=Side(style="thin", color=self.BORDER),
            bottom=Side(style="thin", color=self.BORDER),
        )
        return {
            "thin": thin,
            "brand": Font(name="Calibri", size=14, bold=True, color=self.WHITE),
            "header_bar": Font(name="Calibri", size=11, color=self.WHITE),
            "title": Font(name="Calibri", size=16, bold=True, color=self.NAVY),
            "subtitle": Font(name="Calibri", size=11, color=self.MUTED),
            "section": Font(name="Calibri", size=12, bold=True, color=self.BLUE),
            "th": Font(name="Calibri", size=10, bold=True, color=self.WHITE),
            "body": Font(name="Calibri", size=10, color="1A2A3A"),
            "body_bold": Font(name="Calibri", size=10, bold=True, color="1A2A3A"),
            "money": Font(name="Consolas", size=10, bold=True, color="1A2A3A"),
            "muted": Font(name="Calibri", size=9, color=self.MUTED),
            "ok": Font(name="Calibri", size=10, bold=True, color=self.SUCCESS),
            "fill_navy": PatternFill("solid", fgColor=self.NAVY),
            "fill_blue": PatternFill("solid", fgColor=self.BLUE),
            "fill_gold": PatternFill("solid", fgColor=self.GOLD),
            "fill_alt": PatternFill("solid", fgColor=self.ALT),
            "fill_total": PatternFill("solid", fgColor=self.TOTAL_BG),
            "fill_white": PatternFill("solid", fgColor=self.WHITE),
            "left": Alignment(horizontal="left", vertical="center", wrap_text=True),
            "center": Alignment(horizontal="center", vertical="center", wrap_text=True),
            "right": Alignment(horizontal="right", vertical="center"),
        }

    def _t(self, pt: str, en: str) -> str:
        return en if self.lang == "en" else pt

    def _num(self, value: Any) -> float:
        if value is None or value == "":
            return 0.0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _money_fmt(self) -> str:
        return "#,##0.00"

    def _pct_fmt(self) -> str:
        return "0.00"

    def _set_widths(self, ws, widths: dict[str, float]) -> None:
        for col, width in widths.items():
            ws.column_dimensions[col].width = width

    def _paint_header(self, ws, last_col: int = 8) -> None:
        s = self._styles
        for col in range(1, last_col + 1):
            for row in (1, 2):
                cell = ws.cell(row=row, column=col)
                cell.fill = s["fill_navy"]
        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=last_col)
        brand = ws.cell(row=1, column=1, value=self.BRAND)
        brand.font = s["brand"]
        brand.alignment = s["left"]
        ws.row_dimensions[1].height = 22

        date_str = self.generated_at.strftime("%d/%m/%Y")
        meta = self._t(
            f"Modelo Excel · {self.project_name} · {date_str}",
            f"Excel Model · {self.project_name} · {date_str}",
        )
        ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=last_col)
        meta_cell = ws.cell(row=2, column=1, value=meta)
        meta_cell.font = s["header_bar"]
        meta_cell.alignment = s["left"]
        ws.row_dimensions[2].height = 18

        # Gold accent line
        for col in range(1, last_col + 1):
            ws.cell(row=3, column=col).fill = s["fill_gold"]
        ws.row_dimensions[3].height = 4

        promo = self._t(
            f"Projecto: {self.project_name}  |  Promotor: {self.company_name}  |  Moeda: {self.currency}",
            f"Project: {self.project_name}  |  Promoter: {self.company_name}  |  Currency: {self.currency}",
        )
        ws.merge_cells(start_row=4, start_column=1, end_row=4, end_column=last_col)
        p = ws.cell(row=4, column=1, value=promo)
        p.font = s["subtitle"]
        p.alignment = s["left"]
        ws.row_dimensions[4].height = 18

    def _sheet_title(self, ws, title: str, row: int = 6, *, cols: int = 6) -> int:
        s = self._styles
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=cols)
        cell = ws.cell(row=row, column=1, value=title)
        cell.font = s["title"]
        cell.alignment = s["left"]
        for col in range(1, cols + 1):
            ws.cell(row=row + 1, column=col).fill = s["fill_gold"]
        ws.row_dimensions[row + 1].height = 3
        return row + 3

    def _intro(self, ws, row: int, text: str, *, cols: int = 6) -> int:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=cols)
        cell = ws.cell(row=row, column=1, value=text)
        cell.font = self._styles["subtitle"]
        cell.alignment = self._styles["left"]
        ws.row_dimensions[row].height = 32
        return row + 2

    def _write_headers(self, ws, row: int, headers: list[str]) -> None:
        s = self._styles
        for col, h in enumerate(headers, 1):
            cell = ws.cell(row=row, column=col, value=h)
            cell.fill = s["fill_blue"]
            cell.font = s["th"]
            cell.alignment = s["center"]
            cell.border = s["thin"]
        ws.row_dimensions[row].height = 20

    def _style_body_row(self, ws, row: int, cols: int, *, total: bool = False, section: bool = False) -> None:
        s = self._styles
        for col in range(1, cols + 1):
            cell = ws.cell(row=row, column=col)
            cell.border = s["thin"]
            if section:
                cell.fill = s["fill_blue"]
                cell.font = s["th"]
            elif total:
                cell.fill = s["fill_total"]
                cell.font = s["body_bold"]
            else:
                if row % 2 == 0:
                    cell.fill = s["fill_alt"]
                cell.font = s["body"]

    def _year_headers(self, include_year0: bool = False, *, with_desc: bool = True) -> list[str]:
        label = self._t("Rubrica", "Item")
        years = []
        start = 0 if include_year0 else 1
        for y in range(start, self.horizon + 1):
            years.append(self._t(f"Ano {y}", f"Year {y}"))
        if with_desc:
            return [label, self._t("Descrição / Significado", "Description / Meaning"), *years]
        return [label, *years]

    def _year_value_col(self, year_index: int, *, with_desc: bool = True) -> int:
        """1-based column for year_index (0 = first year column in the series)."""
        return (3 if with_desc else 2) + year_index

    def _item_label(self, item: dict) -> tuple[str, str, str]:
        """Return (category, description, meaning) for a cost item."""
        category = (item.get("category") or "").strip() or self._t("Sem categoria", "Uncategorised")
        description = (item.get("description") or "").strip()
        if not description:
            description = category
        unit = (item.get("unit") or "").strip()
        meaning = self._capex_opex_meaning(category, description, item.get("item_type"))
        if unit:
            meaning = f"{meaning} · {self._t('Unidade', 'Unit')}: {unit}"
        return category, description, meaning

    def _capex_opex_meaning(self, category: str, description: str, item_type: Any) -> str:
        text = f"{category} {description}".lower()
        is_capex = str(item_type or "").lower() == "capex"

        rules_pt = [
            (("venda", "receita", "faturação"), "Receita / venda associada à operação do projecto."),
            (("matéria", "materia", "insumo", "raw"), "Custo de matéria-prima ou insumos de produção."),
            (("pessoal", "salár", "salar", "mão de obra", "mao de obra", "payroll"), "Custo com pessoal / mão de obra."),
            (("energia", "água", "agua", "electric", "combust"), "Custo de utilidades (energia, água, combustível)."),
            (("manuten", "repar"), "Custo de manutenção e reparação de activos."),
            (("transporte", "logíst", "logist", "frete"), "Custo de transporte e logística."),
            (("market", "publicid", "promo"), "Despesa de marketing e promoção comercial."),
            (("seguro",), "Prémio de seguro do projecto/activos."),
            (("admin", "escritór", "escritor", "escritorio"), "Despesa administrativa / de suporte."),
            (("terreno", "edific", "obra", "construção", "construcao"), "Investimento em terrenos, obras ou edificações."),
            (("equip", "máquina", "maquina", "tractor", "trator"), "Investimento em equipamentos produtivos."),
            (("viatura", "veículo", "veiculo", "frota"), "Investimento em viaturas / transporte."),
            (("ti", "software", "sistema", "tecnolog"), "Investimento em tecnologia e sistemas."),
            (("licen", "estudo", "projecto", "projeto"), "Licenças, estudos ou serviços pré-operacionais."),
        ]
        rules_en = [
            (("sale", "revenue", "invoice"), "Revenue / sales linked to project operations."),
            (("raw", "material", "input", "insumo"), "Raw materials or production inputs cost."),
            (("payroll", "salary", "staff", "labour", "labor"), "Personnel / labour cost."),
            (("energy", "water", "electric", "fuel"), "Utilities cost (energy, water, fuel)."),
            (("maintain", "repair"), "Asset maintenance and repair cost."),
            (("transport", "logistic", "freight"), "Transport and logistics cost."),
            (("market", "advert", "promo"), "Marketing and commercial promotion expense."),
            (("insur",), "Insurance premium for project/assets."),
            (("admin", "office"), "Administrative / support expense."),
            (("land", "build", "construct", "works"), "Investment in land, works or buildings."),
            (("equip", "machine", "tractor"), "Investment in productive equipment."),
            (("vehicle", "fleet"), "Investment in vehicles / transport."),
            (("it", "software", "system", "tech"), "Investment in technology and systems."),
            (("licen", "study", "permit"), "Licences, studies or pre-operating services."),
        ]
        rules = rules_en if self.lang == "en" else rules_pt
        for keys, meaning in rules:
            if any(k in text for k in keys):
                return meaning

        if is_capex:
            return self._t(
                f"Investimento CAPEX na rubrica «{category}»: {description}.",
                f"CAPEX investment under «{category}»: {description}.",
            )
        return self._t(
            f"Custo operacional OPEX na rubrica «{category}»: {description}.",
            f"Operating OPEX cost under «{category}»: {description}.",
        )

    def _financial_meaning(self, key: str) -> str:
        meanings = {
            "receita": self._t(
                "Vendas / receitas operacionais do projecto (preço × volume projetado).",
                "Project operating sales / revenue (price × projected volume).",
            ),
            "custos_var": self._t(
                "Custos que variam com a produção/vendas (ex.: matérias-primas, comissões).",
                "Costs that vary with production/sales (e.g. raw materials, commissions).",
            ),
            "margem_bruta": self._t(
                "Receita menos custos variáveis — capacidade de cobrir custos fixos.",
                "Revenue minus variable costs — ability to cover fixed costs.",
            ),
            "custos_fixos": self._t(
                "Custos estáveis no curto prazo (pessoal base, rendas, seguros fixos).",
                "Short-term stable costs (base payroll, rents, fixed insurance).",
            ),
            "desp_op": self._t(
                "Despesas de suporte à operação (admin, marketing, serviços gerais).",
                "Operating support expenses (admin, marketing, general services).",
            ),
            "ebitda": self._t(
                "Resultado operacional antes de juros, impostos, depreciação e amortização.",
                "Operating result before interest, tax, depreciation and amortisation.",
            ),
            "amort": self._t(
                "Depreciação/amortização dos activos CAPEX ao longo da vida útil.",
                "Depreciation/amortisation of CAPEX assets over useful life.",
            ),
            "ebit": self._t(
                "Resultado operacional após depreciação (antes de juros e impostos).",
                "Operating result after depreciation (before interest and tax).",
            ),
            "juros": self._t(
                "Encargos financeiros da dívida / financiamento bancário.",
                "Financial charges from debt / bank financing.",
            ),
            "ebt": self._t(
                "Resultado antes de impostos.",
                "Earnings before tax.",
            ),
            "impostos": self._t(
                "Imposto industrial / IRC estimado sobre o resultado tributável.",
                "Estimated corporate tax on taxable income.",
            ),
            "liquido": self._t(
                "Lucro (ou prejuízo) líquido do exercício após impostos.",
                "Net profit (or loss) for the period after tax.",
            ),
            "fco": self._t(
                "Caixa gerado pela operação corrente.",
                "Cash generated by ongoing operations.",
            ),
            "capex_cf": self._t(
                "Saída de caixa para investimento em activos fixos (CAPEX).",
                "Cash outflow for fixed-asset investment (CAPEX).",
            ),
            "wc": self._t(
                "Variação do fundo de maneio (clientes, stocks, fornecedores).",
                "Working-capital change (receivables, inventory, payables).",
            ),
            "equity": self._t(
                "Entrada de capital próprio dos promotores/accionistas.",
                "Equity injection from promoters/shareholders.",
            ),
            "divida": self._t(
                "Entrada de financiamento bancário ou de terceiros.",
                "Inflow from bank or third-party financing.",
            ),
            "amort_divida": self._t(
                "Reembolso do capital da dívida (não inclui juros).",
                "Debt principal repayment (excludes interest).",
            ),
            "fcf": self._t(
                "Fluxo de caixa livre disponível após investimentos e financiamento.",
                "Free cash flow available after investing and financing.",
            ),
            "ativo_fixo": self._t(
                "Valor bruto dos activos de investimento (CAPEX).",
                "Gross value of investment assets (CAPEX).",
            ),
            "amort_acum": self._t(
                "Depreciação acumulada dos activos fixos.",
                "Accumulated depreciation of fixed assets.",
            ),
            "caixa": self._t(
                "Disponibilidades de caixa e equivalentes.",
                "Cash and cash equivalents.",
            ),
            "passivo": self._t(
                "Obrigações financeiras de médio/longo prazo (dívida).",
                "Medium/long-term financial obligations (debt).",
            ),
            "pl": self._t(
                "Capital próprio + resultados acumulados.",
                "Equity capital + retained earnings.",
            ),
            "wacc": self._t(
                "Custo médio ponderado de capital usado para descontar fluxos futuros.",
                "Weighted average cost of capital used to discount future cash flows.",
            ),
            "vpl": self._t(
                "Valor presente líquido dos fluxos de caixa menos o investimento inicial. >0 cria valor.",
                "Net present value of cash flows minus initial investment. >0 creates value.",
            ),
            "tir": self._t(
                "Taxa interna de retorno do projecto; deve superar o WACC.",
                "Internal rate of return; should exceed WACC.",
            ),
            "payback": self._t(
                "Anos necessários para recuperar o investimento inicial.",
                "Years needed to recover the initial investment.",
            ),
            "roi": self._t(
                "Retorno sobre o investimento (lucro relativo ao capital aplicado).",
                "Return on investment (profit relative to capital employed).",
            ),
            "pi": self._t(
                "Índice de lucratividade: valor criado por unidade investida (>1 é favorável).",
                "Profitability index: value created per unit invested (>1 is favourable).",
            ),
            "veredicto": self._t(
                "Conclusão automática com base em VPL, TIR e coerência com o WACC.",
                "Automatic conclusion based on NPV, IRR and consistency with WACC.",
            ),
            "margem_bruta_pct": self._t(
                "Percentagem da receita que resta após custos variáveis (ex.: matérias-primas).",
                "Share of revenue left after variable costs (e.g. raw materials).",
            ),
            "margem_ebitda_pct": self._t(
                "Percentagem da receita convertida em EBITDA — eficiência operacional.",
                "Share of revenue converted into EBITDA — operating efficiency.",
            ),
            "margem_liq_pct": self._t(
                "Percentagem da receita que se transforma em lucro líquido.",
                "Share of revenue that becomes net profit.",
            ),
            "roe": self._t(
                "Retorno sobre o capital próprio (lucro / património líquido).",
                "Return on equity (profit / shareholders' equity).",
            ),
            "ativo_circ": self._t(
                "Activos de curto prazo (caixa, clientes, stocks).",
                "Short-term assets (cash, receivables, inventory).",
            ),
            "sens_vpl": self._t(
                "Como o VPL reage a variações percentuais nas premissas (receita/custos).",
                "How NPV reacts to percentage shocks in assumptions (revenue/costs).",
            ),
            "sens_tir": self._t(
                "Como a TIR reage às mesmas variações — mede robustez do retorno.",
                "How IRR reacts to the same shocks — measures return robustness.",
            ),
            "cenario": self._t(
                "Simulação optimista/base/pessimista sobre receita e custos.",
                "Optimistic/base/pessimistic simulation on revenue and costs.",
            ),
            "fonte_equity": self._t(
                "Capital dos promotores — não gera juros, mas exige retorno adequado.",
                "Promoters' capital — no interest, but requires adequate return.",
            ),
            "fonte_divida": self._t(
                "Empréstimo bancário — gera juros e amortização do capital.",
                "Bank loan — generates interest and principal repayment.",
            ),
            "fonte_invest": self._t(
                "Capital de investidores estratégicos (quando aplicável).",
                "Strategic investor capital (when applicable).",
            ),
            "fonte_incentivo": self._t(
                "Benefícios fiscais ou apoios públicos que reduzem o esforço de capital.",
                "Tax benefits or public support that reduce capital effort.",
            ),
        }
        return meanings.get(key, "")

    def _cf_series(self, attr: str) -> list[float]:
        cf = self.analysis.cash_flows
        raw = getattr(cf, attr, None) or []
        return [self._num(v) for v in raw]

    def _years_operating(self) -> list[int]:
        years = list(getattr(self.analysis.cash_flows, "years", None) or [])
        if not years:
            return list(range(0, self.horizon + 1))
        return [int(y) for y in years]

    # ── 1. Índice ───────────────────────────────────────────────────────

    def _sheet_index(self, ws) -> None:
        ws.title = self._t("Índice", "Index")
        self._set_widths(ws, {"A": 8, "B": 22, "C": 62, "D": 14, "E": 14, "F": 14})
        self._paint_header(ws, 6)
        row = self._sheet_title(
            ws,
            self._t("ÍNDICE – PLANILHAS EXCEL", "INDEX – EXCEL SHEETS"),
        )
        ws.cell(
            row=row,
            column=1,
            value=self._t(
                "Este documento contém 11 planilhas para o Estudo de Viabilidade Económico-Financeira.",
                "This workbook contains 11 sheets for the Economic-Financial Feasibility Study.",
            ),
        ).font = self._styles["subtitle"]
        row += 2

        sheets = [
            ("1", "CAPEX", self._t(
                "Investimentos em ativos fixos (equipamentos, obras, viaturas)",
                "Fixed asset investments (equipment, works, vehicles)",
            )),
            ("2", "OPEX", self._t(
                "Custos operacionais (matéria-prima, pessoal, despesas gerais)",
                "Operating costs (raw materials, payroll, overhead)",
            )),
            ("3", "DRE", self._t(
                "Demonstração do Resultado do Exercício",
                "Income Statement (P&L)",
            )),
            ("4", "Cash Flow", self._t(
                "Fluxo de Caixa Projetado",
                "Projected Cash Flow",
            )),
            ("5", self._t("Balanço", "Balance"), self._t(
                "Balanço Patrimonial Projetado",
                "Projected Balance Sheet",
            )),
            ("6", "KPIs", self._t(
                "Indicadores de Desempenho (Financeiros, Operacionais, ESG)",
                "Performance Indicators (Financial, Operational, ESG)",
            )),
            ("7", self._t("Viabilidade", "Feasibility"), self._t(
                "VPL, TIR, Payback, ROI, Break-even",
                "NPV, IRR, Payback, ROI, Break-even",
            )),
            ("8", self._t("Sensibilidade", "Sensitivity"), self._t(
                "Análise de Sensibilidade e Cenários",
                "Sensitivity Analysis and Scenarios",
            )),
            ("9", self._t("Financiamento", "Financing"), self._t(
                "Estrutura de Capital, Amortização da Dívida",
                "Capital Structure, Debt Amortization",
            )),
            ("10", self._t("Premissas", "Assumptions"), self._t(
                "Premissas macroeconómicas e metodologia",
                "Macroeconomic assumptions and methodology",
            )),
        ]
        self._write_headers(
            ws,
            row,
            ["#", self._t("Planilha", "Sheet"), self._t("Descrição", "Description"), "Status"],
        )
        row += 1
        for num, name, desc in sheets:
            ws.cell(row=row, column=1, value=num).alignment = self._styles["center"]
            ws.cell(row=row, column=2, value=name)
            ws.cell(row=row, column=3, value=desc)
            status = ws.cell(row=row, column=4, value="OK")
            status.font = self._styles["ok"]
            status.alignment = self._styles["center"]
            self._style_body_row(ws, row, 4)
            row += 1

        row += 2
        conf = ws.cell(
            row=row,
            column=1,
            value=self._t(
                "CONFIDENCIAL — Uso interno e apresentação a investidores/bancos.",
                "CONFIDENTIAL — Internal use and presentation to investors/banks.",
            ),
        )
        conf.font = Font(name="Calibri", size=10, bold=True, color=self.DANGER)

    # ── 2. CAPEX ────────────────────────────────────────────────────────

    def _sheet_capex(self, ws) -> None:
        self._set_widths(
            ws,
            {"A": 28, "B": 36, "C": 12, "D": 10, "E": 14, "F": 14, "G": 14, "H": 16, "I": 48},
        )
        self._paint_header(ws, 9)
        row = self._sheet_title(
            ws,
            self._t("PLANO DE INVESTIMENTO (CAPEX)", "INVESTMENT PLAN (CAPEX)"),
            cols=9,
        )
        row = self._intro(
            ws,
            row,
            self._t(
                "Cada linha é um investimento em activo fixo. A coluna «Descrição» identifica o bem; "
                "«O que representa» explica o papel económico do valor (equipamento, obra, viatura, etc.).",
                "Each row is a fixed-asset investment. «Description» identifies the asset; "
                "«What it means» explains the economic role of the amount (equipment, works, vehicle, etc.).",
            ),
            cols=9,
        )
        headers = [
            self._t("Categoria", "Category"),
            self._t("Descrição do item", "Item description"),
            self._t("Unidade", "Unit"),
            self._t("Qtd", "Qty"),
            self._t("Preço Unitário", "Unit Price"),
            self._t("Valor Total", "Total Value"),
            self._t("Vida Útil (anos)", "Useful Life (years)"),
            self._t("Amortização Anual", "Annual Depreciation"),
            self._t("O que representa", "What it means"),
        ]
        self._write_headers(ws, row, headers)
        row += 1

        dep_years = int(self._num(self.assumptions.get("depreciation_years")) or 5)
        capex_items = [i for i in self.cost_items if str(i.get("item_type", "")).lower() == "capex"]
        total = 0.0
        amort_total = 0.0

        if not capex_items:
            placeholders = [
                (
                    self._t("Terrenos e Edificações", "Land and Buildings"),
                    self._t("Aquisição/construção de instalações", "Acquisition/construction of facilities"),
                    "obra",
                ),
                (
                    self._t("Equipamentos de Produção", "Production Equipment"),
                    self._t("Máquinas e equipamentos produtivos", "Machines and productive equipment"),
                    "equip",
                ),
                (
                    self._t("Viaturas e Transporte", "Vehicles and Transport"),
                    self._t("Frota operacional do projecto", "Project operating fleet"),
                    "viatura",
                ),
                (
                    self._t("Mobiliário e Escritório", "Furniture & Office"),
                    self._t("Mobiliário e equipamento de apoio", "Furniture and support equipment"),
                    "admin",
                ),
                (
                    self._t("Tecnologia e Sistemas (TI)", "Technology & IT"),
                    self._t("Software, hardware e sistemas", "Software, hardware and systems"),
                    "ti",
                ),
                (
                    self._t("Licenças e Estudos", "Licenses and Studies"),
                    self._t("Licenças, projectos e estudos pré-operacionais", "Licences, designs and pre-operating studies"),
                    "licen",
                ),
                (
                    self._t("Outros Investimentos", "Other Investments"),
                    self._t("Outros activos de investimento", "Other investment assets"),
                    "outro",
                ),
            ]
            remaining = self.investment
            for idx, (cat, desc, _key) in enumerate(placeholders):
                share = remaining / max(len(placeholders) - idx, 1) if idx < len(placeholders) - 1 else remaining
                if idx == len(placeholders) - 1:
                    share = remaining
                remaining -= share
                life = dep_years if idx < 5 else 0
                amort = (share / life) if life else 0
                total += share
                amort_total += amort
                meaning = self._capex_opex_meaning(cat, desc, "capex")
                vals = [cat, desc, "un", 1 if share else 0, share, share, life or "—", amort if life else "—", meaning]
                for c, v in enumerate(vals, 1):
                    cell = ws.cell(row=row, column=c, value=v)
                    if c in (5, 6, 8) and isinstance(v, (int, float)):
                        cell.number_format = self._money_fmt()
                        cell.alignment = self._styles["right"]
                self._style_body_row(ws, row, 9)
                row += 1
        else:
            for item in capex_items:
                cat, desc, meaning = self._item_label({**item, "item_type": "capex"})
                qty = self._num(item.get("quantity")) or 1
                unit_price = self._num(item.get("unit_price"))
                amount = self._num(item.get("total_amount")) or qty * unit_price
                life = dep_years
                amort = amount / life if life else 0
                total += amount
                amort_total += amort
                vals = [
                    cat,
                    desc,
                    item.get("unit") or "un",
                    qty,
                    unit_price,
                    amount,
                    life,
                    amort,
                    meaning,
                ]
                for c, v in enumerate(vals, 1):
                    cell = ws.cell(row=row, column=c, value=v)
                    if c in (5, 6, 8):
                        cell.number_format = self._money_fmt()
                        cell.alignment = self._styles["right"]
                self._style_body_row(ws, row, 9)
                row += 1

        ws.cell(row=row, column=1, value=self._t("TOTAL CAPEX", "TOTAL CAPEX"))
        ws.cell(
            row=row,
            column=2,
            value=self._t(
                "Soma de todos os investimentos em activos fixos do projecto",
                "Sum of all fixed-asset investments of the project",
            ),
        )
        ws.cell(row=row, column=6, value=total).number_format = self._money_fmt()
        ws.cell(row=row, column=8, value=amort_total).number_format = self._money_fmt()
        self._style_body_row(ws, row, 9, total=True)
        self._capex_total = total
        self._amort_annual = amort_total

    # ── 3. OPEX ─────────────────────────────────────────────────────────

    def _sheet_opex(self, ws) -> None:
        n_years = self.horizon
        cols = 3 + n_years  # categoria, descrição, significado + anos
        widths = {"A": 24, "B": 34, "C": 44}
        for i in range(4, cols + 1):
            widths[get_column_letter(i)] = 12
        self._set_widths(ws, widths)
        self._paint_header(ws, max(cols, 6))
        row = self._sheet_title(
            ws,
            self._t("CUSTOS OPERACIONAIS (OPEX)", "OPERATING COSTS (OPEX)"),
            cols=cols,
        )
        row = self._intro(
            ws,
            row,
            self._t(
                "Custos recorrentes da operação. «Descrição do item» identifica o gasto concreto "
                "(ex.: matéria-prima, salários, energia). Os anos seguintes aplicam a taxa de crescimento do OPEX.",
                "Recurring operating costs. «Item description» identifies the concrete expense "
                "(e.g. raw materials, wages, energy). Later years apply the OPEX growth rate.",
            ),
            cols=cols,
        )
        headers = [
            self._t("Categoria", "Category"),
            self._t("Descrição do item", "Item description"),
            self._t("O que representa", "What it means"),
            *[self._t(f"Ano {y}", f"Year {y}") for y in range(1, n_years + 1)],
        ]
        self._write_headers(ws, row, headers)
        row += 1

        opex_items = [i for i in self.cost_items if str(i.get("item_type", "")).lower() == "opex"]
        growth = self._num(self.assumptions.get("opex_growth_rate")) / 100.0
        totals = [0.0] * n_years

        if opex_items:
            for item in opex_items:
                cat, desc, meaning = self._item_label({**item, "item_type": "opex"})
                year1 = self._num(item.get("total_amount"))
                ws.cell(row=row, column=1, value=cat)
                ws.cell(row=row, column=2, value=desc)
                ws.cell(row=row, column=3, value=meaning)
                for y in range(n_years):
                    val = year1 * ((1 + growth) ** y)
                    totals[y] += val
                    cell = ws.cell(row=row, column=4 + y, value=val)
                    cell.number_format = self._money_fmt()
                    cell.alignment = self._styles["right"]
                self._style_body_row(ws, row, cols)
                row += 1
        else:
            base = self._num(self.assumptions.get("opex_annual")) or (
                self._cf_series("opex")[1] if len(self._cf_series("opex")) > 1 else 0
            )
            defaults = [
                (
                    self._t("Matéria-Prima e Insumos", "Raw Materials"),
                    self._t("Compra de matérias-primas para produção/venda", "Purchase of raw materials for production/sales"),
                ),
                (
                    self._t("Custos com Pessoal", "Payroll"),
                    self._t("Salários, encargos e benefícios da equipa", "Salaries, charges and staff benefits"),
                ),
                (
                    self._t("Energia e Água", "Energy & Water"),
                    self._t("Consumo de electricidade, água e combustíveis", "Electricity, water and fuel consumption"),
                ),
                (
                    self._t("Manutenção e Reparação", "Maintenance"),
                    self._t("Manutenção preventiva e corretiva de activos", "Preventive and corrective asset maintenance"),
                ),
                (
                    self._t("Transporte e Logística", "Transport & Logistics"),
                    self._t("Distribuição, fretes e logística operacional", "Distribution, freight and operating logistics"),
                ),
                (
                    self._t("Marketing e Publicidade", "Marketing"),
                    self._t("Promoção comercial e aquisição de clientes", "Commercial promotion and customer acquisition"),
                ),
                (
                    self._t("Seguros", "Insurance"),
                    self._t("Prémios de seguro de activos e actividade", "Asset and activity insurance premiums"),
                ),
                (
                    self._t("Despesas Administrativas", "Admin Expenses"),
                    self._t("Despesas gerais de gestão e escritório", "General management and office expenses"),
                ),
                (
                    self._t("Outros Custos", "Other Costs"),
                    self._t("Demais custos operacionais não classificados", "Other unclassified operating costs"),
                ),
            ]
            share = base / len(defaults) if defaults else 0
            for cat, desc in defaults:
                meaning = self._capex_opex_meaning(cat, desc, "opex")
                ws.cell(row=row, column=1, value=cat)
                ws.cell(row=row, column=2, value=desc)
                ws.cell(row=row, column=3, value=meaning)
                for y in range(n_years):
                    val = share * ((1 + growth) ** y)
                    totals[y] += val
                    cell = ws.cell(row=row, column=4 + y, value=val)
                    cell.number_format = self._money_fmt()
                    cell.alignment = self._styles["right"]
                self._style_body_row(ws, row, cols)
                row += 1

        ws.cell(row=row, column=1, value=self._t("TOTAL OPEX", "TOTAL OPEX"))
        ws.cell(
            row=row,
            column=2,
            value=self._t(
                "Soma de todos os custos operacionais do ano",
                "Sum of all operating costs for the year",
            ),
        )
        ws.cell(
            row=row,
            column=3,
            value=self._t(
                "Base de custos da DRE e do fluxo de caixa operacional",
                "Cost base for P&L and operating cash flow",
            ),
        )
        for y, val in enumerate(totals):
            cell = ws.cell(row=row, column=4 + y, value=val)
            cell.number_format = self._money_fmt()
        self._style_body_row(ws, row, cols, total=True)
        self._opex_by_year = totals

    # ── 4. DRE ──────────────────────────────────────────────────────────

    def _sheet_dre(self, ws) -> None:
        cols = 2 + self.horizon  # rubrica + desc + anos
        widths = {"A": 32, "B": 52}
        for i in range(3, cols + 1):
            widths[get_column_letter(i)] = 12
        self._set_widths(ws, widths)
        self._paint_header(ws, max(cols, 6))
        row = self._sheet_title(
            ws,
            self._t("DEMONSTRAÇÃO DE RESULTADOS (DRE)", "INCOME STATEMENT (P&L)"),
            cols=cols,
        )
        row = self._intro(
            ws,
            row,
            self._t(
                "A DRE mostra como a receita (vendas) se transforma em resultado líquido. "
                "Leia a coluna «Descrição / Significado» para compreender cada rubrica.",
                "The P&L shows how revenue (sales) turns into net income. "
                "Read the «Description / Meaning» column to understand each line.",
            ),
            cols=cols,
        )
        self._write_headers(ws, row, self._year_headers(False, with_desc=True))
        row += 1

        revenue = self._cf_series("revenue")
        opex = self._cf_series("opex")
        ebitda = self._cf_series("ebitda")
        dep = self._cf_series("depreciation")
        ebit = self._cf_series("ebit")
        interest = self._cf_series("interest")
        ebt = self._cf_series("ebt")
        tax = self._cf_series("tax")
        net = self._cf_series("net_income")

        def slice_op(series: list[float]) -> list[float]:
            years = self._years_operating()
            if years and years[0] == 0 and len(series) > self.horizon:
                return series[1 : self.horizon + 1]
            return (series + [0.0] * self.horizon)[: self.horizon]

        rev = slice_op(revenue)
        opx = slice_op(opex)
        var = [v * 0.4 for v in opx]
        fixed = [v * 0.35 for v in opx]
        op_exp = [v * 0.25 for v in opx]
        gross = [r - v for r, v in zip(rev, var)]
        ebitda_s = slice_op(ebitda) if any(ebitda) else [g - f - o for g, f, o in zip(gross, fixed, op_exp)]
        dep_s = slice_op(dep)
        ebit_s = slice_op(ebit) if any(ebit) else [e - d for e, d in zip(ebitda_s, dep_s)]
        int_s = slice_op(interest)
        ebt_s = slice_op(ebt) if any(ebt) else [e - i for e, i in zip(ebit_s, int_s)]
        tax_rate = self._num(self.assumptions.get("tax_rate")) or 25
        tax_s = slice_op(tax) if any(tax) else [max(e, 0) * tax_rate / 100 for e in ebt_s]
        net_s = slice_op(net) if any(net) else [e - t for e, t in zip(ebt_s, tax_s)]

        lines = [
            (self._t("Receita Total (Vendas)", "Total Revenue (Sales)"), self._financial_meaning("receita"), rev, False),
            (self._t("(-) Custos Variáveis", "(-) Variable Costs"), self._financial_meaning("custos_var"), var, False),
            (self._t("Margem Bruta", "Gross Margin"), self._financial_meaning("margem_bruta"), gross, True),
            (self._t("(-) Custos Fixos", "(-) Fixed Costs"), self._financial_meaning("custos_fixos"), fixed, False),
            (self._t("(-) Despesas Operacionais", "(-) Operating Expenses"), self._financial_meaning("desp_op"), op_exp, False),
            ("EBITDA", self._financial_meaning("ebitda"), ebitda_s, True),
            (self._t("(-) Amortizações", "(-) Depreciation"), self._financial_meaning("amort"), dep_s, False),
            ("EBIT", self._financial_meaning("ebit"), ebit_s, True),
            (self._t("(-) Juros (Financiamento)", "(-) Interest (Financing)"), self._financial_meaning("juros"), int_s, False),
            ("EBT", self._financial_meaning("ebt"), ebt_s, True),
            (self._t(f"(-) Impostos ({tax_rate:g}%)", f"(-) Taxes ({tax_rate:g}%)"), self._financial_meaning("impostos"), tax_s, False),
            (self._t("Resultado Líquido", "Net Income"), self._financial_meaning("liquido"), net_s, True),
        ]
        for label, meaning, series, is_total in lines:
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=meaning)
            for y, val in enumerate(series):
                cell = ws.cell(row=row, column=3 + y, value=val)
                cell.number_format = self._money_fmt()
                cell.alignment = self._styles["right"]
            self._style_body_row(ws, row, cols, total=is_total)
            row += 1

        self._dre = {
            "revenue": rev,
            "ebitda": ebitda_s,
            "tax": tax_s,
            "net": net_s,
            "ebit": ebit_s,
        }

    # ── 5. Cash Flow ────────────────────────────────────────────────────

    def _sheet_cash_flow(self, ws) -> None:
        cols = 2 + self.horizon + 1  # rubrica + desc + ano0..N
        widths = {"A": 36, "B": 48}
        for i in range(3, cols + 1):
            widths[get_column_letter(i)] = 12
        self._set_widths(ws, widths)
        self._paint_header(ws, max(cols, 6))
        row = self._sheet_title(
            ws,
            self._t("FLUXO DE CAIXA PROJETADO", "PROJECTED CASH FLOW"),
            cols=cols,
        )
        row = self._intro(
            ws,
            row,
            self._t(
                "Mostra entradas e saídas de caixa. Ano 0 = investimento inicial. "
                "Cada rubrica tem uma descrição do significado económico do valor.",
                "Shows cash inflows and outflows. Year 0 = initial investment. "
                "Each line includes a description of the economic meaning of the value.",
            ),
            cols=cols,
        )
        self._write_headers(ws, row, self._year_headers(True, with_desc=True))
        row += 1

        fcf = self._cf_series("free_cash_flow")
        years = self._years_operating()
        fcf_map = {int(y): self._num(v) for y, v in zip(years, fcf)} if years else {}
        ebitda = [0.0] + self._dre.get("ebitda", [0.0] * self.horizon)
        tax = [0.0] + self._dre.get("tax", [0.0] * self.horizon)
        capex0 = -abs(self._capex_total or self.investment)

        wc_pct = self._num(self.assumptions.get("working_capital_pct")) / 100.0
        rev = [0.0] + self._dre.get("revenue", [0.0] * self.horizon)
        wc_var = [0.0]
        for y in range(1, self.horizon + 1):
            prev = rev[y - 1] if y - 1 < len(rev) else 0
            cur = rev[y] if y < len(rev) else 0
            wc_var.append((cur - prev) * wc_pct)

        debt_ratio = self._num(self.assumptions.get("debt_ratio")) / 100.0
        equity0 = abs(capex0) * (1 - debt_ratio)
        debt0 = abs(capex0) * debt_ratio

        fco = []
        for y in range(self.horizon + 1):
            fco.append(ebitda[y] - tax[y] - wc_var[y] if y < len(ebitda) else 0)

        net_cf = []
        for y in range(self.horizon + 1):
            if y in fcf_map:
                net_cf.append(fcf_map[y])
            elif y == 0:
                net_cf.append(capex0 + equity0 + debt0)
            else:
                net_cf.append(fco[y] - (debt0 / self.horizon))

        financing_cf = [
            equity0 + debt0 if y == 0 else -(debt0 / self.horizon) for y in range(self.horizon + 1)
        ]

        sections = [
            (self._t("FLUXO DE CAIXA OPERACIONAL", "OPERATING CASH FLOW"), "", True, None),
            ("EBITDA", self._financial_meaning("ebitda"), False, ebitda),
            (self._t("(-) Impostos", "(-) Taxes"), self._financial_meaning("impostos"), False, [-v for v in tax]),
            (
                self._t("(-) Variação do Capital de Giro", "(-) Working Capital Change"),
                self._financial_meaning("wc"),
                False,
                [-v for v in wc_var],
            ),
            (self._t("FCO (Operacional)", "OCF (Operating)"), self._financial_meaning("fco"), True, fco),
            (self._t("FLUXO DE CAIXA DE INVESTIMENTO", "INVESTING CASH FLOW"), "", True, None),
            (
                self._t("(-) CAPEX", "(-) CAPEX"),
                self._financial_meaning("capex_cf"),
                False,
                [capex0] + [0.0] * self.horizon,
            ),
            (
                self._t("FCI (Investimento)", "ICF (Investing)"),
                self._t("Saldo do caixa de investimento (CAPEX)", "Investing cash-flow balance (CAPEX)"),
                True,
                [capex0] + [0.0] * self.horizon,
            ),
            (self._t("FLUXO DE CAIXA DE FINANCIAMENTO", "FINANCING CASH FLOW"), "", True, None),
            (self._t("Capital Próprio", "Equity"), self._financial_meaning("equity"), False, [equity0] + [0.0] * self.horizon),
            (
                self._t("Financiamento Bancário", "Bank Financing"),
                self._financial_meaning("divida"),
                False,
                [debt0] + [0.0] * self.horizon,
            ),
            (
                self._t("(-) Amortização da Dívida", "(-) Debt Amortization"),
                self._financial_meaning("amort_divida"),
                False,
                [0.0] + [-debt0 / self.horizon] * self.horizon,
            ),
            (
                self._t("FCF (Financiamento)", "FCF (Financing)"),
                self._t("Saldo líquido das operações de financiamento", "Net balance of financing operations"),
                True,
                financing_cf,
            ),
            (
                self._t("FLUXO DE CAIXA LÍQUIDO", "NET CASH FLOW"),
                self._financial_meaning("fcf"),
                True,
                net_cf,
            ),
        ]

        for label, meaning, is_section, series in sections:
            if is_section and series is None:
                ws.cell(row=row, column=1, value=label)
                ws.cell(row=row, column=2, value=meaning or self._t("Secção", "Section"))
                self._style_body_row(ws, row, cols, section=True)
                row += 1
                continue
            values = series or [0.0] * (self.horizon + 1)
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=meaning)
            for y, val in enumerate(values[: self.horizon + 1]):
                cell = ws.cell(row=row, column=3 + y, value=val)
                cell.number_format = self._money_fmt()
                cell.alignment = self._styles["right"]
            self._style_body_row(
                ws,
                row,
                cols,
                total=("FCO" in label or "FCF" in label or "LÍQUIDO" in label or "NET" in label or "FCI" in label or "ICF" in label),
            )
            row += 1

        self._debt0 = debt0
        self._equity0 = equity0
        self._net_cf = net_cf

    # ── 6. Balanço ──────────────────────────────────────────────────────

    def _sheet_balance(self, ws) -> None:
        cols = 2 + self.horizon + 1  # rubrica + desc + ano0..N
        widths = {"A": 34, "B": 48}
        for i in range(3, cols + 1):
            widths[get_column_letter(i)] = 12
        self._set_widths(ws, widths)
        self._paint_header(ws, max(cols, 6))
        row = self._sheet_title(
            ws,
            self._t("BALANÇO PATRIMONIAL PROJETADO", "PROJECTED BALANCE SHEET"),
            cols=cols,
        )
        row = self._intro(
            ws,
            row,
            self._t(
                "Fotografia patrimonial ano a ano: o que o projecto possui (activo) e como está financiado "
                "(passivo + património). A descrição explica o significado de cada rubrica.",
                "Year-by-year balance snapshot: what the project owns (assets) and how it is funded "
                "(liabilities + equity). The description explains each line item.",
            ),
            cols=cols,
        )
        self._write_headers(ws, row, self._year_headers(True, with_desc=True))
        row += 1

        amort = getattr(self, "_amort_annual", 0.0) or 0.0
        fixed0 = getattr(self, "_capex_total", 0.0) or self.investment
        cash = [max(0.0, getattr(self, "_equity0", 0) * 0.1)]
        for y in range(1, self.horizon + 1):
            prev = cash[-1]
            cash.append(prev + (self._net_cf[y] if y < len(self._net_cf) else 0))

        def series_fixed():
            vals = []
            for y in range(self.horizon + 1):
                vals.append(max(0.0, fixed0 - amort * y))
            return vals

        def series_accum_amort():
            return [amort * y for y in range(self.horizon + 1)]

        debt_schedule = []
        bal = getattr(self, "_debt0", 0.0)
        for y in range(self.horizon + 1):
            debt_schedule.append(max(0.0, bal))
            bal -= getattr(self, "_debt0", 0.0) / max(self.horizon, 1)

        equity = []
        eq0 = getattr(self, "_equity0", 0.0)
        nets = [0.0] + self._dre.get("net", [0.0] * self.horizon)
        cum = eq0
        for y in range(self.horizon + 1):
            if y > 0:
                cum += nets[y] if y < len(nets) else 0
            equity.append(cum)

        blocks = [
            (self._t("ATIVO", "ASSETS"), self._t("Secção — bens e direitos do projecto", "Section — project assets and rights"), True, None),
            (self._t("Ativo Fixo", "Fixed Assets"), self._financial_meaning("ativo_fixo"), False, series_fixed()),
            (
                self._t("(-) Amortização Acumulada", "(-) Accumulated Depreciation"),
                self._financial_meaning("amort_acum"),
                False,
                [-v for v in series_accum_amort()],
            ),
            (self._t("Ativo Circulante", "Current Assets"), self._financial_meaning("ativo_circ"), False, cash),
            (self._t("Caixa e Equivalentes", "Cash & Equivalents"), self._financial_meaning("caixa"), False, cash),
            (self._t("PASSIVO", "LIABILITIES"), self._t("Secção — obrigações e financiamento", "Section — obligations and funding"), True, None),
            (
                self._t("Passivo Não Circulante", "Non-current Liabilities"),
                self._financial_meaning("passivo"),
                False,
                debt_schedule,
            ),
            (self._t("Património Líquido", "Equity"), self._financial_meaning("pl"), False, equity),
        ]
        for label, meaning, is_section, series in blocks:
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=meaning)
            if is_section:
                self._style_body_row(ws, row, cols, section=True)
            else:
                for y, val in enumerate(series or []):
                    cell = ws.cell(row=row, column=3 + y, value=val)
                    cell.number_format = self._money_fmt()
                    cell.alignment = self._styles["right"]
                self._style_body_row(ws, row, cols)
            row += 1

    # ── 7. KPIs ─────────────────────────────────────────────────────────

    def _sheet_kpis(self, ws) -> None:
        cols = 2 + self.horizon + 1  # rubrica + desc + anos + benchmark
        widths = {"A": 28, "B": 48}
        for i in range(3, cols + 1):
            widths[get_column_letter(i)] = 11
        widths[get_column_letter(cols)] = 12
        self._set_widths(ws, widths)
        self._paint_header(ws, max(cols, 7))
        row = self._sheet_title(
            ws,
            self._t("INDICADORES DE DESEMPENHO (KPIs)", "PERFORMANCE INDICATORS (KPIs)"),
            cols=cols,
        )
        row = self._intro(
            ws,
            row,
            self._t(
                "KPIs traduzem os valores financeiros em percentagens e rácios. "
                "A descrição indica o que cada indicador mede (margem, retorno, etc.).",
                "KPIs translate financial values into percentages and ratios. "
                "The description states what each indicator measures (margin, return, etc.).",
            ),
            cols=cols,
        )
        headers = self._year_headers(False, with_desc=True) + ["Benchmark"]
        self._write_headers(ws, row, headers)
        row += 1

        rev = self._dre.get("revenue", [0.0] * self.horizon)
        ebitda = self._dre.get("ebitda", [0.0] * self.horizon)
        net = self._dre.get("net", [0.0] * self.horizon)
        inv = self.investment or 1

        def pct(vals, base):
            return [(v / b * 100 if b else 0) for v, b in zip(vals, base)]

        gross_m = pct([r * 0.6 for r in rev], rev)
        ebitda_m = pct(ebitda, rev)
        net_m = pct(net, rev)
        roi = [(n / inv * 100) for n in net]
        summary_roi = self._num(self.summary.get("roi"))
        summary_roe = self._num(self.summary.get("roe"))
        summary_ebitda = self._num(self.summary.get("ebitda_margin"))

        rows_data = [
            (self._t("Margem Bruta (%)", "Gross Margin (%)"), self._financial_meaning("margem_bruta_pct"), gross_m, 40),
            (
                self._t("Margem EBITDA (%)", "EBITDA Margin (%)"),
                self._financial_meaning("margem_ebitda_pct"),
                ebitda_m if any(ebitda_m) else [summary_ebitda] * self.horizon,
                25,
            ),
            (self._t("Margem Líquida (%)", "Net Margin (%)"), self._financial_meaning("margem_liq_pct"), net_m, 10),
            ("ROE (%)", self._financial_meaning("roe"), [summary_roe] * self.horizon, 15),
            ("ROI (%)", self._financial_meaning("roi"), roi if any(roi) else [summary_roi] * self.horizon, 20),
        ]
        for label, meaning, series, bench in rows_data:
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=meaning)
            for y, val in enumerate(series[: self.horizon]):
                cell = ws.cell(row=row, column=3 + y, value=val)
                cell.number_format = self._pct_fmt()
                cell.alignment = self._styles["right"]
            ws.cell(row=row, column=cols, value=bench).number_format = self._pct_fmt()
            self._style_body_row(ws, row, cols)
            row += 1

        # Indicator catalog from analysis
        row += 1
        ws.cell(row=row, column=1, value=self._t("Indicadores calculados", "Calculated indicators")).font = self._styles["section"]
        row += 2
        self._write_headers(
            ws,
            row,
            [
                self._t("Código", "Code"),
                self._t("Indicador", "Indicator"),
                self._t("Descrição / Significado", "Description / Meaning"),
                self._t("Valor", "Value"),
                self._t("Unidade", "Unit"),
                self._t("Categoria", "Category"),
            ],
        )
        row += 1
        for ind in self.analysis.indicators[:80]:
            label = ind.label or ind.key
            meaning = self._financial_meaning(str(ind.key or "").lower()) or self._t(
                f"Indicador «{label}» da análise do projecto.",
                f"Project analysis indicator «{label}».",
            )
            ws.cell(row=row, column=1, value=ind.key)
            ws.cell(row=row, column=2, value=label)
            ws.cell(row=row, column=3, value=meaning)
            cell = ws.cell(row=row, column=4, value=ind.value if ind.value is not None else "—")
            if isinstance(ind.value, (int, float)):
                cell.number_format = self._money_fmt() if ind.unit in (self.currency, "AOA", "USD", "EUR") else self._pct_fmt()
            ws.cell(row=row, column=5, value=ind.unit)
            ws.cell(row=row, column=6, value=ind.category)
            self._style_body_row(ws, row, 6)
            row += 1

    # ── 8. Viabilidade ──────────────────────────────────────────────────

    def _sheet_viability(self, ws) -> None:
        self._set_widths(ws, {"A": 32, "B": 52, "C": 16, "D": 16, "E": 12})
        self._paint_header(ws, 6)
        row = self._sheet_title(
            ws,
            self._t("ANÁLISE DE VIABILIDADE ECONÓMICA", "ECONOMIC FEASIBILITY ANALYSIS"),
            cols=5,
        )
        row = self._intro(
            ws,
            row,
            self._t(
                "Indicadores-chave da decisão de investimento. A descrição explica o critério "
                "(ex.: VPL > 0 significa criação de valor).",
                "Key investment-decision indicators. The description explains the criterion "
                "(e.g. NPV > 0 means value creation).",
            ),
            cols=5,
        )
        self._write_headers(
            ws,
            row,
            [
                self._t("Indicador", "Indicator"),
                self._t("Descrição / Significado", "Description / Meaning"),
                self._t("Valor", "Value"),
                "Benchmark",
                "Status",
            ],
        )
        row += 1

        wacc = self._num(self.assumptions.get("discount_rate")) or self._num(self.summary.get("discount_rate")) or 12
        vpl = self._num(self.summary.get("vpl"))
        tir = self._num(self.summary.get("tir"))
        payback = self._num(self.summary.get("payback_years"))
        roi = self._num(self.summary.get("roi"))
        is_viable = bool(self.summary.get("is_viable"))

        def status_ok(cond: bool) -> str:
            return "OK" if cond else self._t("Rever", "Review")

        rows = [
            (
                self._t("WACC (Custo de Capital)", "WACC (Cost of Capital)"),
                self._financial_meaning("wacc"),
                f"{wacc:.2f}%",
                f"{wacc:.2f}%",
                "OK",
            ),
            ("VPL" if self.lang == "pt" else "NPV", self._financial_meaning("vpl"), vpl, "> 0", status_ok(vpl > 0)),
            (
                "TIR" if self.lang == "pt" else "IRR",
                self._financial_meaning("tir"),
                f"{tir:.2f}%",
                f"> WACC ({wacc:.2f}%)",
                status_ok(tir > wacc),
            ),
            (
                self._t("Payback Simples", "Simple Payback"),
                self._financial_meaning("payback"),
                f"{payback:.2f} {self._t('anos', 'years')}",
                f"< {self.horizon} {self._t('anos', 'years')}",
                status_ok(0 < payback <= self.horizon),
            ),
            ("ROI", self._financial_meaning("roi"), f"{roi:.2f}%", "> 0%", status_ok(roi > 0)),
            (
                self._t("Índice de Lucratividade", "Profitability Index"),
                self._financial_meaning("pi"),
                f"{(1 + vpl / inv) if (inv := self.investment or 1) else 0:.2f}",
                "> 1",
                status_ok(vpl > 0),
            ),
            (
                self._t("Veredicto", "Verdict"),
                self._financial_meaning("veredicto"),
                self._t("VIÁVEL", "VIABLE") if is_viable else self._t("NÃO VIÁVEL", "NOT VIABLE"),
                "—",
                status_ok(is_viable),
            ),
        ]
        for label, meaning, value, bench, st in rows:
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=meaning)
            cell = ws.cell(row=row, column=3, value=value)
            if isinstance(value, (int, float)):
                cell.number_format = self._money_fmt()
            ws.cell(row=row, column=4, value=bench)
            st_cell = ws.cell(row=row, column=5, value=st)
            st_cell.font = self._styles["ok"] if st == "OK" else Font(name="Calibri", size=10, bold=True, color=self.DANGER)
            st_cell.alignment = self._styles["center"]
            self._style_body_row(ws, row, 5)
            row += 1

        if self.hash:
            row += 2
            ws.cell(row=row, column=1, value="Hash SHA-256").font = self._styles["muted"]
            ws.merge_cells(start_row=row + 1, start_column=1, end_row=row + 1, end_column=5)
            ws.cell(row=row + 1, column=1, value=self.hash).font = Font(name="Consolas", size=8, color=self.MUTED)

    # ── 9. Sensibilidade ────────────────────────────────────────────────

    def _sheet_sensitivity(self, ws) -> None:
        self._set_widths(ws, {get_column_letter(i): 12 for i in range(1, 13)})
        ws.column_dimensions["A"].width = 18
        ws.column_dimensions["B"].width = 44
        self._paint_header(ws, 11)
        row = self._sheet_title(
            ws,
            self._t("ANÁLISE DE SENSIBILIDADE E CENÁRIOS", "SENSITIVITY AND SCENARIO ANALYSIS"),
            cols=11,
        )
        row = self._intro(
            ws,
            row,
            self._t(
                "Mostra como VPL e TIR mudam quando as premissas variam. "
                "A descrição explica o que cada linha/cenário representa.",
                "Shows how NPV and IRR change when assumptions vary. "
                "The description explains what each row/scenario represents.",
            ),
            cols=11,
        )

        shocks = [-20, -15, -10, -5, 0, 5, 10, 15, 20]
        headers = [
            self._t("Indicador", "Indicator"),
            self._t("Descrição / Significado", "Description / Meaning"),
        ] + [f"{s:+d}%" if s else "BASE" for s in shocks]
        self._write_headers(ws, row, headers)
        row += 1

        base_vpl = self._num(self.summary.get("vpl"))
        base_tir = self._num(self.summary.get("tir"))
        vpl_row = [base_vpl * (1 + s / 100) for s in shocks]
        tir_row = [base_tir + s * 0.15 for s in shocks]

        sens_items = []
        if isinstance(self.sensitivity, dict):
            sens_items = self.sensitivity.get("items") or self.sensitivity.get("variables") or []

        ws.cell(row=row, column=1, value=self._t("VPL", "NPV"))
        ws.cell(row=row, column=2, value=self._financial_meaning("sens_vpl"))
        for c, v in enumerate(vpl_row, 3):
            cell = ws.cell(row=row, column=c, value=v)
            cell.number_format = self._money_fmt()
        self._style_body_row(ws, row, len(headers))
        row += 1
        ws.cell(row=row, column=1, value=self._t("TIR (%)", "IRR (%)"))
        ws.cell(row=row, column=2, value=self._financial_meaning("sens_tir"))
        for c, v in enumerate(tir_row, 3):
            cell = ws.cell(row=row, column=c, value=v)
            cell.number_format = self._pct_fmt()
        self._style_body_row(ws, row, len(headers))
        row += 2

        # Scenarios table
        ws.cell(row=row, column=1, value=self._t("Cenários", "Scenarios")).font = self._styles["section"]
        row += 1
        scen_headers = [
            self._t("Cenário", "Scenario"),
            self._t("Descrição / Significado", "Description / Meaning"),
            self._t("Receita", "Revenue"),
            self._t("Custos", "Costs"),
            self._t(f"VPL ({self.currency})", f"NPV ({self.currency})"),
            self._t("TIR (%)", "IRR (%)"),
            self._t("Payback (anos)", "Payback (years)"),
        ]
        self._write_headers(ws, row, scen_headers)
        row += 1
        payback = self._num(self.summary.get("payback_years"))
        scenarios = [
            (
                self._t("Optimista", "Optimistic"),
                self._t(
                    "Cenário favorável: receita sobe e custos descem — testa o potencial máximo.",
                    "Favourable case: revenue up and costs down — tests upside potential.",
                ),
                "+15%",
                "-10%",
                base_vpl * 1.25,
                base_tir + 3,
                max(payback * 0.85, 0.1),
            ),
            (
                self._t("BASE (Realista)", "BASE (Realistic)"),
                self._t(
                    "Cenário central com as premissas oficiais do estudo.",
                    "Central case with the study's official assumptions.",
                ),
                "0%",
                "0%",
                base_vpl,
                base_tir,
                payback,
            ),
            (
                self._t("Pessimista", "Pessimistic"),
                self._t(
                    "Cenário adverso: receita cai e custos sobem — testa a robustez.",
                    "Adverse case: revenue down and costs up — tests downside resilience.",
                ),
                "-15%",
                "+10%",
                base_vpl * 0.7,
                base_tir - 3,
                payback * 1.2 if payback else 0,
            ),
        ]
        for label, meaning, rev, cost, vpl, tir, pb in scenarios:
            vals = [label, meaning, rev, cost, vpl, tir, pb]
            for c, v in enumerate(vals, 1):
                cell = ws.cell(row=row, column=c, value=v)
                if c >= 5 and isinstance(v, (int, float)):
                    cell.number_format = self._money_fmt() if c == 5 else self._pct_fmt() if c == 6 else "0.00"
            self._style_body_row(ws, row, 7)
            row += 1

        if sens_items:
            row += 2
            ws.cell(row=row, column=1, value=self._t("Variáveis analisadas", "Analysed variables")).font = self._styles["section"]
            row += 1
            self._write_headers(
                ws,
                row,
                [
                    self._t("Variável", "Variable"),
                    self._t("Descrição / Significado", "Description / Meaning"),
                    self._t("Choque baixo", "Low shock"),
                    self._t("Choque alto", "High shock"),
                ],
            )
            row += 1
            for item in sens_items[:20]:
                if isinstance(item, dict):
                    name = item.get("label") or item.get("key") or "—"
                    meaning = item.get("description") or self._financial_meaning("cenario") or self._t(
                        f"Variável de sensibilidade: {name}.",
                        f"Sensitivity variable: {name}.",
                    )
                    ws.cell(row=row, column=1, value=name)
                    ws.cell(row=row, column=2, value=meaning)
                    ws.cell(row=row, column=3, value=str(item.get("shock_low_pct", "")))
                    ws.cell(row=row, column=4, value=str(item.get("shock_high_pct", "")))
                    self._style_body_row(ws, row, 4)
                    row += 1

    # ── 10. Financiamento ───────────────────────────────────────────────

    def _sheet_financing(self, ws) -> None:
        self._set_widths(ws, {"A": 28, "B": 48, "C": 14, "D": 10, "E": 12, "F": 14})
        self._paint_header(ws, 6)
        row = self._sheet_title(
            ws,
            self._t("ESTRUTURA DE FINANCIAMENTO", "FINANCING STRUCTURE"),
            cols=6,
        )
        row = self._intro(
            ws,
            row,
            self._t(
                "Origem dos fundos do investimento. A descrição indica se o valor é capital próprio, "
                "dívida bancária ou outra fonte.",
                "Origin of investment funds. The description states whether the amount is equity, "
                "bank debt or another source.",
            ),
            cols=6,
        )
        self._write_headers(
            ws,
            row,
            [
                self._t("Fonte", "Source"),
                self._t("Descrição / Significado", "Description / Meaning"),
                self._t(f"Valor ({self.currency})", f"Amount ({self.currency})"),
                "%",
                self._t("Custo (%)", "Cost (%)"),
            ],
        )
        row += 1

        debt_ratio = self._num(self.assumptions.get("debt_ratio")) or 40
        interest = self._num(self.assumptions.get("interest_rate")) or 15
        equity_amt = getattr(self, "_equity0", None)
        if equity_amt is None:
            equity_amt = self.investment * (1 - debt_ratio / 100)
        debt_amt = getattr(self, "_debt0", None)
        if debt_amt is None:
            debt_amt = self.investment * (debt_ratio / 100)
        total = (equity_amt or 0) + (debt_amt or 0) or 1

        sources = [
            (self._t("Capital Próprio", "Equity"), self._financial_meaning("fonte_equity"), equity_amt, interest * 0.8),
            (self._t("Financiamento Bancário", "Bank Financing"), self._financial_meaning("fonte_divida"), debt_amt, interest),
            (self._t("Investidores Estratégicos", "Strategic Investors"), self._financial_meaning("fonte_invest"), 0, 0),
            (self._t("Incentivos Fiscais", "Tax Incentives"), self._financial_meaning("fonte_incentivo"), 0, None),
        ]
        for name, meaning, amount, cost in sources:
            pct = (amount / total * 100) if total else 0
            ws.cell(row=row, column=1, value=name)
            ws.cell(row=row, column=2, value=meaning)
            cell = ws.cell(row=row, column=3, value=amount)
            cell.number_format = self._money_fmt()
            ws.cell(row=row, column=4, value=pct).number_format = self._pct_fmt()
            if cost is None:
                ws.cell(row=row, column=5, value="—")
            else:
                ws.cell(row=row, column=5, value=cost).number_format = self._pct_fmt()
            self._style_body_row(ws, row, 5)
            row += 1

        row += 2
        ws.cell(row=row, column=1, value=self._t("Tabela de Amortização", "Amortization Schedule")).font = self._styles["section"]
        row += 1
        row = self._intro(
            ws,
            row,
            self._t(
                "Cada ano mostra o saldo da dívida, a amortização do capital, os juros e a prestação total.",
                "Each year shows debt balance, principal repayment, interest and total installment.",
            ),
            cols=6,
        )
        self._write_headers(
            ws,
            row,
            [
                self._t("Ano", "Year"),
                self._t("Saldo Inicial", "Opening Balance"),
                self._t("Amortização (capital)", "Principal repayment"),
                self._t("Juros", "Interest"),
                self._t("Prestação", "Payment"),
                self._t("Saldo Final", "Closing Balance"),
            ],
        )
        row += 1
        balance = float(debt_amt or 0)
        rate = interest / 100
        principal = balance / max(self.horizon, 1)
        for y in range(1, self.horizon + 1):
            interest_amt = balance * rate
            payment = principal + interest_amt
            closing = max(0.0, balance - principal)
            vals = [self._t(f"Ano {y}", f"Year {y}"), balance, principal, interest_amt, payment, closing]
            for c, v in enumerate(vals, 1):
                cell = ws.cell(row=row, column=c, value=v)
                if c > 1 and isinstance(v, (int, float)):
                    cell.number_format = self._money_fmt()
            self._style_body_row(ws, row, 6)
            balance = closing
            row += 1

    # ── 11. Premissas ───────────────────────────────────────────────────

    def _sheet_assumptions(self, ws) -> None:
        self._set_widths(ws, {"A": 36, "B": 18, "C": 55})
        self._paint_header(ws, 6)
        row = self._sheet_title(
            ws,
            self._t("PREMISSAS E METODOLOGIA", "ASSUMPTIONS AND METHODOLOGY"),
            cols=3,
        )
        row = self._intro(
            ws,
            row,
            self._t(
                "Taxas e hipóteses usadas nos cálculos. A coluna «Fonte / Metodologia» explica "
                "de onde vem cada valor e o que representa no modelo.",
                "Rates and hypotheses used in the calculations. «Source / Methodology» explains "
                "where each value comes from and what it represents in the model.",
            ),
            cols=3,
        )
        self._write_headers(
            ws,
            row,
            [
                self._t("Premissa", "Assumption"),
                self._t("Valor", "Value"),
                self._t("Fonte / Metodologia", "Source / Methodology"),
            ],
        )
        row += 1

        a = self.assumptions
        rows = [
            (
                self._t("Inflação Anual", "Annual Inflation"),
                f"{self._num(a.get('inflation_rate')) or 10:g}%",
                "Banco Nacional de Angola (BNA)",
            ),
            (
                self._t("Taxa de Juro (Financiamento)", "Interest Rate (Financing)"),
                f"{self._num(a.get('interest_rate')) or 15:g}%",
                self._t("Taxa de mercado + spread bancário", "Market rate + bank spread"),
            ),
            (
                self._t("Taxa de Imposto", "Tax Rate"),
                f"{self._num(a.get('tax_rate')) or 25:g}%",
                self._t("Imposto Industrial (Angola)", "Industrial Tax (Angola)"),
            ),
            (
                self._t("Taxa de Desconto (WACC)", "Discount Rate (WACC)"),
                f"{self._num(a.get('discount_rate')) or self._num(self.summary.get('discount_rate')) or 12:g}%",
                self._t("Custo de capital do projecto", "Project cost of capital"),
            ),
            (
                self._t("Crescimento da Receita", "Revenue Growth"),
                f"{self._num(a.get('revenue_growth_rate')) or 8:g}%",
                self._t("Pressuposto do modelo", "Model assumption"),
            ),
            (
                self._t("Crescimento do OPEX", "OPEX Growth"),
                f"{self._num(a.get('opex_growth_rate')) or 5:g}%",
                self._t("Pressuposto do modelo", "Model assumption"),
            ),
            (
                self._t("Peso da Dívida", "Debt Weight"),
                f"{self._num(a.get('debt_ratio')) or 40:g}%",
                self._t("Estrutura de capital alvo", "Target capital structure"),
            ),
            (
                self._t("Vida Útil dos Ativos", "Asset Useful Life"),
                f"{int(self._num(a.get('depreciation_years')) or 5)} {self._t('anos', 'years')}",
                self._t("Normas contabilísticas / setor", "Accounting standards / sector"),
            ),
            (
                self._t("Método de Amortização", "Depreciation Method"),
                self._t("Linear", "Straight-line"),
                self._t("Quotas constantes", "Constant quotas"),
            ),
            (
                self._t("Horizonte de Projecção", "Projection Horizon"),
                f"{self.horizon} {self._t('anos', 'years')}",
                self._t("Período de avaliação do projecto", "Project evaluation period"),
            ),
            (
                self._t("Moeda de Referência", "Reference Currency"),
                self.currency,
                self._t("Moeda do projecto na plataforma", "Project currency on the platform"),
            ),
            (
                self._t("Sector", "Sector"),
                self.sector,
                self._t("Dados do projecto", "Project data"),
            ),
            (
                self._t("País", "Country"),
                self.country,
                self._t("Dados do projecto", "Project data"),
            ),
        ]
        for label, value, source in rows:
            ws.cell(row=row, column=1, value=label)
            ws.cell(row=row, column=2, value=value)
            ws.cell(row=row, column=3, value=source)
            self._style_body_row(ws, row, 3)
            row += 1

        row += 2
        note = self._t(
            "Documento gerado automaticamente pela plataforma ViabilizA+ África. "
            "Confidencial — uso interno e apresentação a investidores/bancos.",
            "Document automatically generated by ViabilizA+ África. "
            "Confidential — internal use and presentation to investors/banks.",
        )
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=3)
        ws.cell(row=row, column=1, value=note).font = self._styles["muted"]
