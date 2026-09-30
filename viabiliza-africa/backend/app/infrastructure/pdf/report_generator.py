from app.application.dto.report_data import ReportDataBundle
from app.domain.enums.report_type import ReportType
from app.infrastructure.pdf.bda_report import BdaReportPdf
from app.infrastructure.pdf.bfa_report import BfaReportPdf
from app.infrastructure.pdf.international_report import InternationalReportPdf


class ReportPdfGenerator:
    """Fachada para geração de PDFs institucionais (Strategy)."""

    def generate(
        self,
        report_type: ReportType,
        data: ReportDataBundle,
        *,
        verification_url: str,
        qr_image_b64: str | None,
        print_optimized: bool = False,
    ) -> bytes:
        kwargs = {
            "data": data,
            "verification_url": verification_url,
            "qr_image_b64": qr_image_b64,
        }
        if report_type == ReportType.INTERNATIONAL:
            return InternationalReportPdf(**kwargs).build()
        if report_type == ReportType.BFA:
            return BfaReportPdf(**kwargs).build()
        if report_type == ReportType.BDA:
            return BdaReportPdf(**kwargs).build()
        raise ValueError(f"Tipo de relatório não suportado: {report_type}")
