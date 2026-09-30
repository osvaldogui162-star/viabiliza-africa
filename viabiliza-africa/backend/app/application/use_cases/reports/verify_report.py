from app.application.use_cases.reports.mappers import to_report_output
from app.domain.exceptions.domain_exceptions import EntityNotFoundError
from app.domain.repositories.report_repository import IReportRepository


class VerifyReportUseCase:
    """Verificação pública de relatório via QR Code."""

    def __init__(self, report_repository: IReportRepository) -> None:
        self._reports = report_repository

    def execute(self, verification_hash: str) -> dict:
        report = self._reports.find_by_verification_hash(verification_hash)
        if report is None:
            raise EntityNotFoundError("Relatório", verification_hash)
        data = to_report_output(report)
        data["valid"] = True
        data["message"] = "Relatório autêntico — ViabilizA+ África"
        return data
