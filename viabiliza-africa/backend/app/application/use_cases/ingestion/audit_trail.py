from uuid import UUID

from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.use_cases.ingestion.mappers import to_audit_output
from app.domain.enums.audit_entity_type import AuditEntityType
from app.domain.exceptions.domain_exceptions import ValidationError
from app.domain.repositories.audit_trail_repository import IAuditTrailRepository


class GetAuditTrailUseCase:
    """UC18 — Visualizar audit trail."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        audit_trail_repository: IAuditTrailRepository,
    ) -> None:
        self._ctx = context_resolver
        self._audit = audit_trail_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        entity_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        self._ctx.require_audit_view(ctx)

        parsed_type = None
        if entity_type:
            try:
                parsed_type = AuditEntityType(entity_type)
            except ValueError as exc:
                raise ValidationError(f"entity_type inválido: {entity_type}") from exc

        entries = self._audit.find_by_project(
            project_id, entity_type=parsed_type, limit=limit, offset=offset
        )
        total = self._audit.count_by_project(project_id, entity_type=parsed_type)
        return {
            "items": [to_audit_output(e) for e in entries],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
