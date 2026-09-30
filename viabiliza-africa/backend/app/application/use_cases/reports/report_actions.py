import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.application.interfaces.email_service import IEmailService
from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.services.report_access_policy import ReportAccessPolicy
from app.application.services.subscription_service import SubscriptionService
from app.application.use_cases.reports.mappers import to_report_output, to_submission_output
from app.config import Config
from app.domain.enums.audit_action import AuditAction
from app.domain.enums.audit_entity_type import AuditEntityType
from app.domain.enums.bank_code import BankCode
from app.domain.exceptions.domain_exceptions import (
    AuthorizationError,
    EntityNotFoundError,
    ValidationError,
)
from app.domain.repositories.audit_trail_repository import IAuditTrailRepository
from app.domain.repositories.report_repository import (
    IBankSubmissionRepository,
    IReportRepository,
    IReportShareRepository,
)
from app.infrastructure.bank.bank_api_client import BankApiClient


class ListReportsUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        report_policy: ReportAccessPolicy,
        report_repository: IReportRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = report_policy
        self._reports = report_repository

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_download(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para listar relatórios")
        items = self._reports.find_by_project(project_id)
        return {"items": [to_report_output(r) for r in items], "total": len(items)}


class GetReportUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        report_policy: ReportAccessPolicy,
        report_repository: IReportRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = report_policy
        self._reports = report_repository

    def execute(self, *, actor_id: UUID, project_id: UUID, report_id: UUID) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_download(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão")
        report = self._reports.find_by_id(report_id)
        if report is None or report.project_id != project_id:
            raise EntityNotFoundError("Relatório", str(report_id))
        return to_report_output(report)


class DownloadReportUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        report_policy: ReportAccessPolicy,
        report_repository: IReportRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = report_policy
        self._reports = report_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        report_id: UUID,
        inline: bool = False,
    ) -> tuple[bytes, str, bool]:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_download(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para descarregar relatórios")
        report = self._reports.find_by_id(report_id)
        if report is None or report.project_id != project_id:
            raise EntityNotFoundError("Relatório", str(report_id))
        content = self._reports.read_pdf_bytes(report.pdf_storage_path)
        filename = f"relatorio_{report.report_type.value}_{report.id}.pdf"
        return content, filename, inline


class SendReportEmailUseCase:
    """UC04 / UC31 — Enviar relatório por email (PDF anexo + auditoria)."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        report_policy: ReportAccessPolicy,
        report_repository: IReportRepository,
        email_service: IEmailService,
        audit_repository: IAuditTrailRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = report_policy
        self._reports = report_repository
        self._email = email_service
        self._audit = audit_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        report_id: UUID,
        to_email: str,
        subject: str | None = None,
        message: str | None = None,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_send_email_or_whatsapp(ctx.actor, ctx.project):
            raise AuthorizationError("Não tem permissão para enviar relatórios por email")

        report = self._reports.find_by_id(report_id)
        if report is None or report.project_id != project_id:
            raise EntityNotFoundError("Relatório", str(report_id))

        recipient = to_email.strip().lower()
        if not recipient or "@" not in recipient:
            raise ValidationError("Email de destino inválido")

        is_en = report.language.value == "en"
        default_subject = f"ViabilizA+ África — {report.title}"
        resolved_subject = (subject or "").strip() or default_subject
        if is_en and not (subject or "").strip():
            resolved_subject = f"ViabilizA+ África — {report.title}"

        if (message or "").strip():
            body = message.strip()
        elif is_en:
            body = f"Please find attached the report «{report.title}» for project {ctx.project.name}."
        else:
            body = f"Segue em anexo o relatório «{report.title}» do projecto {ctx.project.name}."

        pdf = self._reports.read_pdf_bytes(report.pdf_storage_path)
        filename = f"relatorio_{report.report_type.value}_{report.id}.pdf"

        if is_en:
            body_html = (
                "<div style='font-family:Segoe UI,Arial,sans-serif;color:#18181b;line-height:1.55'>"
                f"<p>Hello,</p>"
                f"<p>{body.replace(chr(10), '<br/>')}</p>"
                "<p style='margin-top:20px;padding:14px 16px;background:#ecfdf5;border-radius:10px;"
                "border:1px solid #a7f3d0'>"
                f"<strong>Attachment:</strong> {filename}<br/>"
                f"<strong>Project:</strong> {ctx.project.name}<br/>"
                f"<strong>Type:</strong> {report.report_type.label()} · {report.language.value.upper()} · {report.currency}<br/>"
                f"<strong>SHA-256 Hash:</strong> "
                f"<span style='font-family:monospace;font-size:12px'>{report.verification_hash}</span>"
                "</p>"
                "<p style='color:#71717a;font-size:12px;margin-top:24px'>"
                "Document generated and sent by ViabilizA+ África platform."
                "</p></div>"
            )
            body_text = (
                f"{body}\n\n"
                f"Attachment: {filename}\n"
                f"Project: {ctx.project.name}\n"
                f"Hash: {report.verification_hash}\n"
            )
        else:
            body_html = (
                "<div style='font-family:Segoe UI,Arial,sans-serif;color:#18181b;line-height:1.55'>"
                f"<p>Olá,</p>"
                f"<p>{body.replace(chr(10), '<br/>')}</p>"
                "<p style='margin-top:20px;padding:14px 16px;background:#ecfdf5;border-radius:10px;"
                "border:1px solid #a7f3d0'>"
                f"<strong>Anexo:</strong> {filename}<br/>"
                f"<strong>Projecto:</strong> {ctx.project.name}<br/>"
                f"<strong>Tipo:</strong> {report.report_type.label()} · {report.language.value.upper()} · {report.currency}<br/>"
                f"<strong>Hash SHA-256:</strong> "
                f"<span style='font-family:monospace;font-size:12px'>{report.verification_hash}</span>"
                "</p>"
                "<p style='color:#71717a;font-size:12px;margin-top:24px'>"
                "Documento gerado e enviado pela plataforma ViabilizA+ África."
                "</p></div>"
            )
            body_text = (
                f"{body}\n\n"
                f"Anexo: {filename}\n"
                f"Projecto: {ctx.project.name}\n"
                f"Hash: {report.verification_hash}\n"
            )

        from datetime import datetime, timezone

        sent_at = datetime.now(timezone.utc).isoformat()

        # Auditoria imediata; SMTP em background para a UI não ficar à espera
        self._audit.create(
            project_id=project_id,
            entity_type=AuditEntityType.REPORT,
            entity_id=report.id,
            action=AuditAction.REPORT_SENT_EMAIL,
            actor_id=actor_id,
            data_hash=report.verification_hash,
            metadata={
                "to": recipient,
                "recipient": recipient,
                "subject": resolved_subject,
                "sent_at": sent_at,
                "report_title": report.title,
                "report_type": report.report_type.value,
                "filename": filename,
                "file_size_bytes": len(pdf),
                "delivery": "async",
            },
        )

        send_async = getattr(self._email, "send_report_email_async", None)
        if callable(send_async):
            send_async(
                recipient,
                subject=resolved_subject,
                body_html=body_html,
                body_text=body_text,
                pdf_bytes=pdf,
                filename=filename,
            )
        else:
            self._email.send_report_email(
                recipient,
                subject=resolved_subject,
                body_html=body_html,
                body_text=body_text,
                pdf_bytes=pdf,
                filename=filename,
            )

        return {
            "message": "Relatório a enviar por email (anexo PDF)",
            "to": recipient,
            "subject": resolved_subject,
            "sent_at": sent_at,
            "verification_hash": report.verification_hash,
            "async": True,
        }


class ShareReportWhatsAppUseCase:
    """UC32 — Link temporário (7 dias) para WhatsApp."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        report_policy: ReportAccessPolicy,
        report_repository: IReportRepository,
        share_repository: IReportShareRepository,
        audit_repository: IAuditTrailRepository,
        config: Config,
    ) -> None:
        self._ctx = context_resolver
        self._policy = report_policy
        self._reports = report_repository
        self._shares = share_repository
        self._audit = audit_repository
        self._config = config

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        report_id: UUID,
        phone: str | None = None,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_send_email_or_whatsapp(ctx.actor, ctx.project):
            raise AuthorizationError("Não tem permissão para partilhar relatórios")

        report = self._reports.find_by_id(report_id)
        if report is None or report.project_id != project_id:
            raise EntityNotFoundError("Relatório", str(report_id))

        token = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(days=self._config.REPORT_SHARE_DAYS)
        link = self._shares.create(
            report_id=report.id,
            token=token,
            expires_at=expires,
            created_by=actor_id,
        )

        share_url = f"{self._config.REPORT_SHARE_BASE_URL}/{token}"
        text = f"Relatório ViabilizA+ África: {report.title}\n{share_url}"
        whatsapp_url = f"{self._config.WHATSAPP_SHARE_BASE_URL}{text.replace(' ', '%20')}"
        if phone:
            whatsapp_url = f"https://wa.me/{phone.lstrip('+')}?text={text.replace(' ', '%20')}"

        self._audit.create(
            project_id=project_id,
            entity_type=AuditEntityType.REPORT,
            entity_id=report.id,
            action=AuditAction.REPORT_SHARED,
            actor_id=actor_id,
            data_hash=report.verification_hash,
            metadata={"expires_at": expires.isoformat()},
        )

        return {
            "share_url": share_url,
            "whatsapp_url": whatsapp_url,
            "expires_at": link.expires_at.isoformat(),
            "valid_days": self._config.REPORT_SHARE_DAYS,
        }


class SubmitReportToBankUseCase:
    """UC34 — Enviar relatório para banco via API."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        report_policy: ReportAccessPolicy,
        report_repository: IReportRepository,
        bank_repository: IBankSubmissionRepository,
        bank_client: BankApiClient,
        audit_repository: IAuditTrailRepository,
        subscription_service: SubscriptionService | None = None,
    ) -> None:
        self._ctx = context_resolver
        self._policy = report_policy
        self._reports = report_repository
        self._banks = bank_repository
        self._client = bank_client
        self._audit = audit_repository
        self._subscriptions = subscription_service

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        report_id: UUID,
        bank_code: str,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_submit_to_bank(ctx.actor, ctx.project):
            raise AuthorizationError("Não tem permissão para submeter a bancos")

        if not BankCode.is_valid(bank_code):
            raise ValidationError(f"Banco inválido. Valores: {', '.join(BankCode.values())}")

        if self._subscriptions:
            self._subscriptions.ensure_bank_api(ctx.actor)

        report = self._reports.find_by_id(report_id)
        if report is None or report.project_id != project_id:
            raise EntityNotFoundError("Relatório", str(report_id))

        project_payload = {
            "id": str(ctx.project.id),
            "name": ctx.project.name,
            "company": ctx.project.company_name,
            "tax_id": ctx.project.company_tax_id,
            "sector": ctx.project.sector.value,
            "country": ctx.project.country.value,
            "investment": str(ctx.project.investment_amount),
        }

        result = self._client.submit(
            BankCode(bank_code),
            project_payload=project_payload,
            report_hash=report.verification_hash,
            pdf_size=report.file_size_bytes,
        )

        submission = self._banks.create(
            report_id=report.id,
            project_id=project_id,
            bank_code=BankCode(bank_code),
            status=result.get("status", "submitted"),
            request_payload=project_payload,
            response_payload=result,
            external_ref=result.get("external_ref"),
            submitted_by=actor_id,
        )

        self._audit.create(
            project_id=project_id,
            entity_type=AuditEntityType.REPORT,
            entity_id=report.id,
            action=AuditAction.REPORT_SUBMITTED_BANK,
            actor_id=actor_id,
            data_hash=report.verification_hash,
            metadata={"bank": bank_code, "ref": result.get("external_ref")},
        )

        return to_submission_output(submission)


class PrintReportUseCase:
    """UC06 — Impressão com registo em auditoria."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        report_policy: ReportAccessPolicy,
        report_repository: IReportRepository,
        audit_repository: IAuditTrailRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = report_policy
        self._reports = report_repository
        self._audit = audit_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        report_id: UUID,
    ) -> tuple[bytes, str]:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_download(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para imprimir relatórios")

        report = self._reports.find_by_id(report_id)
        if report is None or report.project_id != project_id:
            raise EntityNotFoundError("Relatório", str(report_id))

        self._audit.create(
            project_id=project_id,
            entity_type=AuditEntityType.REPORT,
            entity_id=report.id,
            action=AuditAction.REPORT_PRINTED,
            actor_id=actor_id,
            data_hash=report.verification_hash,
        )

        content = self._reports.read_pdf_bytes(report.pdf_storage_path)
        filename = f"relatorio_{report.report_type.value}_{report.id}.pdf"
        return content, filename


class GetSharedReportUseCase:
    """Download público via token WhatsApp (UC32)."""

    def __init__(
        self,
        share_repository: IReportShareRepository,
        report_repository: IReportRepository,
    ) -> None:
        self._shares = share_repository
        self._reports = report_repository

    def execute(self, *, token: str) -> tuple[bytes, str]:
        link = self._shares.find_by_token(token)
        if link is None:
            raise EntityNotFoundError("Link", token)
        if link.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise ValidationError("Link expirado (validade de 7 dias)")

        report = self._reports.find_by_id(link.report_id)
        if report is None:
            raise EntityNotFoundError("Relatório", str(link.report_id))

        content = self._reports.read_pdf_bytes(report.pdf_storage_path)
        filename = f"relatorio_{report.report_type.value}.pdf"
        return content, filename
