import base64
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.application.dto.report_data import ReportDataBundle


class PdfReportBuilder:
    """Base para relatórios PDF institucionais."""

    INSTITUTIONAL_BLUE = colors.HexColor("#1F4E79")
    INSTITUTIONAL_GOLD = colors.HexColor("#C5A572")
    LIGHT_GREY = colors.HexColor("#F5F5F5")

    def __init__(self, data: ReportDataBundle, *, verification_url: str, qr_image_b64: str | None):
        self.data = data
        self.verification_url = verification_url
        self.qr_image_b64 = qr_image_b64
        self.lang = data.report_language
        self.currency = data.report_currency
        self.styles = getSampleStyleSheet()
        self._setup_styles()
        self.elements: list = []

    def _setup_styles(self) -> None:
        self.styles.add(
            ParagraphStyle(
                name="CoverTitle",
                parent=self.styles["Title"],
                fontSize=22,
                textColor=self.INSTITUTIONAL_BLUE,
                alignment=TA_CENTER,
                spaceAfter=20,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="SectionHeader",
                parent=self.styles["Heading1"],
                fontSize=14,
                textColor=self.INSTITUTIONAL_BLUE,
                spaceBefore=16,
                spaceAfter=10,
                borderPadding=4,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="BodyJustify",
                parent=self.styles["Normal"],
                fontSize=10,
                alignment=TA_JUSTIFY,
                leading=14,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="Footer",
                parent=self.styles["Normal"],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER,
            )
        )

    def _t(self, pt: str, en: str) -> str:
        return pt if self.lang == "pt" else en

    def _money(self, amount) -> str:
        from decimal import Decimal

        from app.application.services.report_data_aggregator import ReportDataAggregator

        val = float(amount) * self.data.exchange_rate
        return ReportDataAggregator.format_money(val, self.currency, self.lang)

    def add_cover(self, title: str, subtitle: str, normative: str) -> None:
        p = self.data.project
        self.elements.append(Spacer(1, 2 * cm))
        self.elements.append(Paragraph("ViabilizA+ África", self.styles["CoverTitle"]))
        self.elements.append(Paragraph(title, self.styles["CoverTitle"]))
        self.elements.append(Spacer(1, 0.5 * cm))
        self.elements.append(Paragraph(subtitle, self.styles["Heading2"]))
        self.elements.append(Spacer(1, 1 * cm))
        info = [
            [self._t("Projeto:", "Project:"), p.name],
            [self._t("Empresa:", "Company:"), p.company_name],
            [self._t("NIF:", "Tax ID:"), p.company_tax_id or "—"],
            [self._t("País:", "Country:"), p.country],
            [self._t("Setor:", "Sector:"), p.sector],
            [self._t("Moeda relatório:", "Report currency:"), self.currency],
            [self._t("Data:", "Date:"), datetime.now().strftime("%d/%m/%Y")],
            [self._t("Normativa:", "Regulation:"), normative],
        ]
        t = Table(info, colWidths=[4 * cm, 12 * cm])
        t.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ("BACKGROUND", (0, 0), (-1, -1), self.LIGHT_GREY),
                    ("BOX", (0, 0), (-1, -1), 0.5, self.INSTITUTIONAL_BLUE),
                ]
            )
        )
        self.elements.append(t)
        self.elements.append(PageBreak())

    def add_section(self, number: int, title: str, body: str) -> None:
        self.elements.append(
            Paragraph(f"{number}. {title}", self.styles["SectionHeader"])
        )
        self.elements.append(Paragraph(body, self.styles["BodyJustify"]))
        self.elements.append(Spacer(1, 0.3 * cm))

    def add_table(self, headers: list[str], rows: list[list], col_widths: list | None = None) -> None:
        data = [headers] + rows
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), self.INSTITUTIONAL_BLUE),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, self.LIGHT_GREY]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        self.elements.append(t)
        self.elements.append(Spacer(1, 0.4 * cm))

    def add_qr_verification_page(self) -> None:
        self.elements.append(PageBreak())
        self.elements.append(
            Paragraph(
                self._t("Verificação de Autenticidade", "Authenticity Verification"),
                self.styles["SectionHeader"],
            )
        )
        self.elements.append(
            Paragraph(
                self._t(
                    "Este relatório foi gerado pela plataforma ViabilizA+ África com rastreabilidade "
                    "total dos dados. Utilize o QR Code ou o link abaixo para verificar a integridade.",
                    "This report was generated by ViabilizA+ África with full data traceability. "
                    "Use the QR Code or link below to verify integrity.",
                ),
                self.styles["BodyJustify"],
            )
        )
        if self.qr_image_b64:
            try:
                raw = base64.b64decode(self.qr_image_b64.split(",")[-1])
                img = Image(io.BytesIO(raw), width=4 * cm, height=4 * cm)
                self.elements.append(Spacer(1, 0.5 * cm))
                self.elements.append(img)
            except Exception:
                pass
        self.elements.append(Spacer(1, 0.3 * cm))
        self.elements.append(Paragraph(self.verification_url, self.styles["Normal"]))

    def build_pdf(self) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
            title=self.data.project.name,
        )

        def footer(canvas, doc):
            canvas.saveState()
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(colors.grey)
            text = self._t(
                f"ViabilizA+ África — Confidencial — Pág. {doc.page}",
                f"ViabilizA+ África — Confidential — Page {doc.page}",
            )
            canvas.drawCentredString(A4[0] / 2, 15 * mm, text)
            canvas.restoreState()

        doc.build(self.elements, onFirstPage=footer, onLaterPages=footer)
        return buffer.getvalue()
