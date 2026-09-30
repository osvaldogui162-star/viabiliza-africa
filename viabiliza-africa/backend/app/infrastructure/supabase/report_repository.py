import os
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

from supabase import Client

from app.domain.entities.report import BankReportSubmission, Report, ReportShareLink
from app.domain.enums.bank_code import BankCode
from app.domain.enums.report_language import ReportLanguage
from app.domain.enums.report_type import ReportType
from app.domain.repositories.report_repository import (
    IBankSubmissionRepository,
    IReportRepository,
    IReportShareRepository,
)
from app.infrastructure.supabase.response_helpers import get_rows, get_single_row


def _parse_dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _map_report(row: dict) -> Report:
    return Report(
        id=UUID(row["id"]),
        project_id=UUID(row["project_id"]),
        report_type=ReportType(row["report_type"]),
        language=ReportLanguage(row["language"]),
        currency=row["currency"],
        title=row["title"],
        verification_hash=row["verification_hash"],
        pdf_storage_path=row["pdf_storage_path"],
        file_size_bytes=row["file_size_bytes"],
        qr_code_data=row.get("qr_code_data"),
        qr_code_image=row.get("qr_code_image"),
        metadata=row.get("metadata") or {},
        generated_by=UUID(row["generated_by"]),
        created_at=_parse_dt(row["created_at"]),
    )


class FileReportStorage:
    """Armazenamento local de PDFs (pode migrar para Supabase Storage)."""

    def __init__(self, base_dir: str | None = None) -> None:
        self._base = Path(base_dir or os.getenv("REPORT_STORAGE_DIR", "storage/reports"))
        self._base.mkdir(parents=True, exist_ok=True)

    def write(self, relative_path: str, content: bytes) -> None:
        path = self._base / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def read(self, relative_path: str) -> bytes:
        return (self._base / relative_path).read_bytes()


class SupabaseReportRepository(IReportRepository):
    TABLE = "reports"

    def __init__(self, client: Client, storage: FileReportStorage | None = None) -> None:
        self._client = client
        self._storage = storage or FileReportStorage()

    def find_by_id(self, report_id: UUID) -> Report | None:
        response = (
            self._client.table(self.TABLE).select("*").eq("id", str(report_id)).limit(1).execute()
        )
        row = get_single_row(response)
        return _map_report(row) if row else None

    def find_by_project(self, project_id: UUID, *, limit: int = 20) -> list[Report]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("project_id", str(project_id))
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return [_map_report(r) for r in get_rows(response)]

    def find_by_verification_hash(self, verification_hash: str) -> Report | None:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("verification_hash", verification_hash)
            .limit(1)
            .execute()
        )
        row = get_single_row(response)
        return _map_report(row) if row else None

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
        payload = {
            "project_id": str(project_id),
            "report_type": report_type.value,
            "language": language.value,
            "currency": currency,
            "title": title,
            "verification_hash": verification_hash,
            "pdf_storage_path": pdf_storage_path,
            "file_size_bytes": file_size_bytes,
            "qr_code_data": qr_code_data,
            "qr_code_image": qr_code_image,
            "metadata": metadata,
            "generated_by": str(generated_by),
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        return _map_report(row)

    def read_pdf_bytes(self, storage_path: str) -> bytes:
        return self._storage.read(storage_path)

    def write_pdf_bytes(self, storage_path: str, content: bytes) -> None:
        self._storage.write(storage_path, content)

    def store_pdf(self, project_id: UUID, content: bytes) -> str:
        rel = f"{project_id}/{uuid4()}.pdf"
        self.write_pdf_bytes(rel, content)
        return rel


class SupabaseReportShareRepository(IReportShareRepository):
    TABLE = "report_share_links"

    def __init__(self, client: Client) -> None:
        self._client = client

    def find_by_token(self, token: str) -> ReportShareLink | None:
        response = (
            self._client.table(self.TABLE).select("*").eq("token", token).limit(1).execute()
        )
        row = get_single_row(response)
        if not row:
            return None
        return ReportShareLink(
            id=UUID(row["id"]),
            report_id=UUID(row["report_id"]),
            token=row["token"],
            expires_at=_parse_dt(row["expires_at"]),
            created_by=UUID(row["created_by"]),
            created_at=_parse_dt(row["created_at"]),
        )

    def create(
        self,
        *,
        report_id: UUID,
        token: str,
        expires_at: datetime,
        created_by: UUID,
    ) -> ReportShareLink:
        payload = {
            "report_id": str(report_id),
            "token": token,
            "expires_at": expires_at.isoformat(),
            "created_by": str(created_by),
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        return ReportShareLink(
            id=UUID(row["id"]),
            report_id=UUID(row["report_id"]),
            token=row["token"],
            expires_at=_parse_dt(row["expires_at"]),
            created_by=UUID(row["created_by"]),
            created_at=_parse_dt(row["created_at"]),
        )


class SupabaseBankSubmissionRepository(IBankSubmissionRepository):
    TABLE = "bank_report_submissions"

    def __init__(self, client: Client) -> None:
        self._client = client

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
        payload = {
            "report_id": str(report_id),
            "project_id": str(project_id),
            "bank_code": bank_code.value,
            "status": status,
            "request_payload": request_payload,
            "response_payload": response_payload,
            "external_ref": external_ref,
            "submitted_by": str(submitted_by),
        }
        response = self._client.table(self.TABLE).insert(payload).execute()
        row = get_single_row(response)
        return BankReportSubmission(
            id=UUID(row["id"]),
            report_id=UUID(row["report_id"]),
            project_id=UUID(row["project_id"]),
            bank_code=BankCode(row["bank_code"]),
            status=row["status"],
            request_payload=row["request_payload"],
            response_payload=row["response_payload"],
            external_ref=row.get("external_ref"),
            submitted_by=UUID(row["submitted_by"]),
            created_at=_parse_dt(row["created_at"]),
        )

    def find_by_project(self, project_id: UUID, *, limit: int = 20) -> list[BankReportSubmission]:
        response = (
            self._client.table(self.TABLE)
            .select("*")
            .eq("project_id", str(project_id))
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        results = []
        for row in get_rows(response):
            results.append(
                BankReportSubmission(
                    id=UUID(row["id"]),
                    report_id=UUID(row["report_id"]),
                    project_id=UUID(row["project_id"]),
                    bank_code=BankCode(row["bank_code"]),
                    status=row["status"],
                    request_payload=row["request_payload"],
                    response_payload=row["response_payload"],
                    external_ref=row.get("external_ref"),
                    submitted_by=UUID(row["submitted_by"]),
                    created_at=_parse_dt(row["created_at"]),
                )
            )
        return results
