from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.enums.bank_code import BankCode
from app.domain.enums.report_language import ReportLanguage
from app.domain.enums.report_type import ReportType


@dataclass
class Report:
    id: UUID
    project_id: UUID
    report_type: ReportType
    language: ReportLanguage
    currency: str
    title: str
    verification_hash: str
    pdf_storage_path: str
    file_size_bytes: int
    qr_code_data: str | None
    qr_code_image: str | None
    metadata: dict
    generated_by: UUID
    created_at: datetime


@dataclass
class ReportShareLink:
    id: UUID
    report_id: UUID
    token: str
    expires_at: datetime
    created_by: UUID
    created_at: datetime


@dataclass
class BankReportSubmission:
    id: UUID
    report_id: UUID
    project_id: UUID
    bank_code: BankCode
    status: str
    request_payload: dict
    response_payload: dict
    external_ref: str | None
    submitted_by: UUID
    created_at: datetime
