from datetime import datetime
from uuid import UUID

from app.application.dto.auth_dto import AccessLogOutput
from app.domain.enums.access_action import AccessAction
from app.domain.exceptions.domain_exceptions import AuthorizationError, EntityNotFoundError
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.user_repository import IUserRepository


class GetAccessLogsUseCase:
    """UC05 — Ver log de acessos (apenas Administrador)."""

    def __init__(
        self,
        user_repository: IUserRepository,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._users = user_repository
        self._access_logs = access_log_repository

    def execute(
        self,
        *,
        admin_user_id: UUID,
        user_id: UUID | None = None,
        action: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        admin = self._users.find_by_id(admin_user_id)
        if admin is None:
            raise EntityNotFoundError("Utilizador", str(admin_user_id))
        if not admin.can_view_access_logs():
            raise AuthorizationError("Apenas administradores podem consultar logs de acesso")

        parsed_action = AccessAction(action) if action else None

        logs = self._access_logs.find_all(
            user_id=user_id,
            action=parsed_action,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            offset=offset,
        )
        total = self._access_logs.count(
            user_id=user_id,
            action=parsed_action,
            from_date=from_date,
            to_date=to_date,
        )

        return {
            "items": [
                AccessLogOutput(
                    id=log.id,
                    user_id=log.user_id,
                    action=log.action.value,
                    ip_address=log.ip_address,
                    user_agent=log.user_agent,
                    metadata=log.metadata,
                    created_at=log.created_at,
                )
                for log in logs
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
