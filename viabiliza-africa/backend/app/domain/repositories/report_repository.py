from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.entities.report import BankReportSubmission, Report, ReportShareLink
from app.domain.enums.bank_code import BankCode
from app.domain.enums.report_language import ReportLanguage
from app.domain.enums.report_type import ReportType


class IReportRepository(ABC):
    @abstractmethod
    def find_by_id(self, report_id: UUID) -> Report | None:
        ...

    @abstractmethod
    def find_by_project(self, project_id: UUID, *, limit: int = 20) -> list[Report]:
        ...

    @abstractmethod
    def find_by_verification_hash(self, verification_hash: str) -> Report | None:
        ...

    @abstractmethod
    def create(
        self,
        *,
        project_id: UUID,
        report_type: ReportType,
        language: ReportLanguage,
        currency: str,
        title: str,
        verification_hash: str,
        pdf_storage_path: str,
        file_size_bytes: int,
        qr_code_data: str | None,
        qr_code_image: str | None,
        metadata: dict,
        generated_by: UUID,
    ) -> Report:
        ...

    @abstractmethod
    def read_pdf_bytes(self, storage_path: str) -> bytes:
        ...

    @abstractmethod
    def write_pdf_bytes(self, storage_path: str, content: bytes) -> None:
        ...

    @abstractmethod
    def store_pdf(self, project_id: UUID, content: bytes) -> str:
        ...


class IReportShareRepository(ABC):
    @abstractmethod
    def find_by_token(self, token: str) -> ReportShareLink | None:
        ...

    @abstractmethod
    def create(
        self,
        *,
        report_id: UUID,
        token: str,
        expires_at: datetime,
        created_by: UUID,
    ) -> ReportShareLink:
        ...


class IBankSubmissionRepository(ABC):
    @abstractmethod
    def create(
        self,
        *,
        report_id: UUID,
        project_id: UUID,
        bank_code: BankCode,
        status: str,
        request_payload: dict,
        response_payload: dict,
        external_ref: str | None,
        submitted_by: UUID,
    ) -> BankReportSubmission:
        ...

    @abstractmethod
    def find_by_project(self, project_id: UUID, *, limit: int = 20) -> list[BankReportSubmission]:
        ...
