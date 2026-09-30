from app.domain.entities.report import BankReportSubmission, Report


def to_report_output(report: Report) -> dict:
    return {
        "id": str(report.id),
        "project_id": str(report.project_id),
        "report_type": report.report_type.value,
        "report_type_label": report.report_type.label(),
        "language": report.language.value,
        "currency": report.currency,
        "title": report.title,
        # Relatório persistido = pronto para download (entidade Report não tem coluna status)
        "status": "ready",
        "verification_hash": report.verification_hash,
        "file_size_bytes": report.file_size_bytes,
        "qr_code_data": report.qr_code_data,
        "metadata": report.metadata,
        "generated_by": str(report.generated_by),
        "created_at": report.created_at.isoformat(),
    }


def to_submission_output(sub: BankReportSubmission) -> dict:
    return {
        "id": str(sub.id),
        "report_id": str(sub.report_id),
        "project_id": str(sub.project_id),
        "bank_code": sub.bank_code.value,
        "status": sub.status,
        "external_ref": sub.external_ref,
        "response": sub.response_payload,
        "created_at": sub.created_at.isoformat(),
    }
