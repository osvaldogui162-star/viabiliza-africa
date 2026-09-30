from datetime import datetime
from uuid import UUID

from app.application.services.admin_access_policy import AdminAccessPolicy
from app.application.use_cases.ingestion.mappers import to_audit_output
from app.domain.enums.audit_action import AuditAction
from app.domain.enums.audit_entity_type import AuditEntityType
from app.domain.exceptions.domain_exceptions import ValidationError
from app.domain.repositories.audit_trail_repository import IAuditTrailRepository


class GetGlobalAuditTrailUseCase:
    """UC38 — Consultar logs de auditoria completos (todos os projectos)."""

    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        audit_repository: IAuditTrailRepository,
    ) -> None:
        self._policy = admin_policy
        self._audit = audit_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID | None = None,
        filter_actor_id: UUID | None = None,
        entity_type: str | None = None,
        action: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        self._policy.require_admin(actor_id)

        parsed_entity = None
        if entity_type:
            try:
                parsed_entity = AuditEntityType(entity_type)
            except ValueError as exc:
                raise ValidationError(f"entity_type inválido: {entity_type}") from exc

        parsed_action = None
        if action:
            try:
                parsed_action = AuditAction(action)
            except ValueError as exc:
                raise ValidationError(f"action inválida: {action}") from exc

        entries = self._audit.find_global(
            project_id=project_id,
            actor_id=filter_actor_id,
            entity_type=parsed_entity,
            action=parsed_action,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            offset=offset,
        )
        total = self._audit.count_global(
            project_id=project_id,
            actor_id=filter_actor_id,
            entity_type=parsed_entity,
            action=parsed_action,
            from_date=from_date,
            to_date=to_date,
        )
        return {
            "items": [to_audit_output(e) for e in entries],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
