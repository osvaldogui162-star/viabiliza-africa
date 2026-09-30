import json
from uuid import UUID

from app.application.interfaces.hash_service import IHashService
from app.application.interfaces.qr_code_service import IQRCodeService
from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.services.report_access_policy import ReportAccessPolicy
from app.application.services.subscription_service import SubscriptionService
from app.application.services.report_data_aggregator import ReportDataAggregator
from app.application.services.report_prerequisites_validator import ReportPrerequisitesValidator
from app.application.use_cases.reports.mappers import to_report_output
from app.config import Config
from app.domain.enums.audit_action import AuditAction
from app.domain.enums.audit_entity_type import AuditEntityType
from app.domain.enums.report_language import ReportLanguage
from app.domain.enums.report_type import ReportType
from app.domain.exceptions.domain_exceptions import AuthorizationError, ValidationError
from app.domain.repositories.audit_trail_repository import IAuditTrailRepository
from app.application.services.notification_service import NotificationService
from app.domain.repositories.project_share_repository import IProjectShareRepository
from app.domain.repositories.report_repository import IReportRepository
from app.infrastructure.pdf.report_generator import ReportPdfGenerator


class GenerateReportUseCase:
    """UC28, UC29, UC30 — Gerar relatórios PDF institucionais."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        report_policy: ReportAccessPolicy,
        aggregator: ReportDataAggregator,
        prerequisites: ReportPrerequisitesValidator,
        report_repository: IReportRepository,
        pdf_generator: ReportPdfGenerator,
        hash_service: IHashService,
        qr_service: IQRCodeService,
        audit_repository: IAuditTrailRepository,
        config: Config,
        subscription_service: SubscriptionService | None = None,
        notification_service: NotificationService | None = None,
        project_share_repository: IProjectShareRepository | None = None,
    ) -> None:
        self._ctx = context_resolver
        self._policy = report_policy
        self._aggregator = aggregator
        self._prerequisites = prerequisites
        self._reports = report_repository
        self._pdf = pdf_generator
        self._hash = hash_service
        self._qr = qr_service
        self._audit = audit_repository
        self._config = config
        self._subscriptions = subscription_service
        self._notifications = notification_service
        self._shares = project_share_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        report_type: str,
        language: str = "pt",
        currency: str = "AOA",
        print_optimized: bool = False,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_generate(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para gerar relatórios")

        if not ReportType.is_valid(report_type):
            raise ValidationError(f"Tipo inválido. Valores: {', '.join(ReportType.values())}")
        if not ReportLanguage.is_valid(language):
            raise ValidationError(f"Idioma inválido. Valores: {', '.join(ReportLanguage.values())}")
        if currency not in ("USD", "EUR", "AOA"):
            raise ValidationError("Moeda deve ser USD, EUR ou AOA")

        rtype = ReportType(report_type)
        if self._subscriptions:
            self._subscriptions.ensure_report_type(ctx.actor, rtype)

        self._prerequisites.validate(project_id, rtype, currency=currency)

        data = self._aggregator.aggregate(
            project_id, report_currency=currency, report_language=language
        )

        if not data.indicators and rtype != ReportType.BDA:
            raise ValidationError(
                "Execute o cálculo de indicadores (Módulo 4) antes de gerar o relatório"
            )

        hash_input = json.dumps(
            {
                "project_id": str(project_id),
                "type": report_type,
                "language": language,
                "currency": currency,
                "summary": data.indicators_summary,
            },
            sort_keys=True,
        )
        verification_hash = self._hash.hash_string(hash_input)
        verify_url = f"{self._config.FRONTEND_BASE_URL}/verify/report/{verification_hash}"
        qr = self._qr.generate(verify_url)

        pdf_bytes = self._pdf.generate(
            rtype,
            data,
            verification_url=verify_url,
            qr_image_b64=qr.image_base64,
            print_optimized=print_optimized,
        )

        storage_path = self._reports.store_pdf(project_id, pdf_bytes)
        title = f"{rtype.label()} — {ctx.project.name}"

        report = self._reports.create(
            project_id=project_id,
            report_type=rtype,
            language=ReportLanguage(language),
            currency=currency,
            title=title,
            verification_hash=verification_hash,
            pdf_storage_path=storage_path,
            file_size_bytes=len(pdf_bytes),
            qr_code_data=qr.data,
            qr_code_image=qr.image_base64,
            metadata={
                "sections": 10 if rtype == ReportType.INTERNATIONAL else None,
                "print_optimized": print_optimized,
                "indicators_count": len(data.indicators),
            },
            generated_by=actor_id,
        )

        self._audit.create(
            project_id=project_id,
            entity_type=AuditEntityType.REPORT,
            entity_id=report.id,
            action=AuditAction.REPORT_GENERATED,
            actor_id=actor_id,
            data_hash=verification_hash,
            metadata={"report_type": report_type},
        )

        if self._notifications:
            notify_ids = [ctx.project.owner_id]
            if self._shares:
                notify_ids.extend(s.user_id for s in self._shares.find_by_project(project_id))
            for uid in {u for u in notify_ids if u != actor_id}:
                self._notifications.notify(
                    user_id=uid,
                    type="report_ready",
                    title="Relatório gerado",
                    body=f"{rtype.label()} — {ctx.project.name}",
                    href=f"/projects/{project_id}",
                    project_id=project_id,
                )

        output = to_report_output(report)
        output["download_url"] = f"/api/v1/projects/{project_id}/reports/{report.id}/download"
        return output
