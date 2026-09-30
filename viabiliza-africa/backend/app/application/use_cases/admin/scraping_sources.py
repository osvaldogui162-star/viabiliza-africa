from uuid import UUID

from app.application.services.admin_access_policy import AdminAccessPolicy
from app.application.use_cases.admin.mappers import to_scraping_source_output
from app.domain.enums.access_action import AccessAction
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, ValidationError
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.admin_config_repository import IScrapingSourceAdminRepository


class ListScrapingSourcesAdminUseCase:
    """UC35 — Listar fontes de scraping (admin)."""

    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: IScrapingSourceAdminRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository

    def execute(self, *, actor_id: UUID) -> dict:
        self._policy.require_admin(actor_id)
        items = self._repo.find_all()
        return {"items": [to_scraping_source_output(s) for s in items], "total": len(items)}


class CreateScrapingSourceUseCase:
    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: IScrapingSourceAdminRepository,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository
        self._logs = access_log_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        code: str,
        name: str,
        base_url: str,
        description: str | None = None,
        country: str = "AO",
        config: dict | None = None,
        is_active: bool = True,
    ) -> dict:
        self._policy.require_admin(actor_id)
        if not code.strip():
            raise ValidationError("Código é obrigatório")
        if self._repo.find_by_code(code.strip().lower()):
            raise ValidationError(f"Fonte «{code}» já existe")

        source = self._repo.create(
            code=code,
            name=name,
            base_url=base_url,
            description=description,
            country=country,
            config=config or {},
            is_active=is_active,
            updated_by=actor_id,
        )
        self._logs.create(
            user_id=actor_id,
            action=AccessAction.CONFIG_UPDATED,
            metadata={"type": "scraping_source", "action": "created", "code": source.code},
        )
        return to_scraping_source_output(source)


class UpdateScrapingSourceUseCase:
    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: IScrapingSourceAdminRepository,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository
        self._logs = access_log_repository

    def execute(self, *, actor_id: UUID, source_id: UUID, **kwargs) -> dict:
        self._policy.require_admin(actor_id)
        existing = self._repo.find_by_id(source_id)
        if existing is None:
            raise EntityNotFoundError("Fonte de scraping", str(source_id))

        source = self._repo.update(source_id, updated_by=actor_id, **kwargs)
        self._logs.create(
            user_id=actor_id,
            action=AccessAction.CONFIG_UPDATED,
            metadata={"type": "scraping_source", "action": "updated", "code": source.code},
        )
        return to_scraping_source_output(source)


class DeleteScrapingSourceUseCase:
    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: IScrapingSourceAdminRepository,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository
        self._logs = access_log_repository

    def execute(self, *, actor_id: UUID, source_id: UUID) -> dict:
        self._policy.require_admin(actor_id)
        existing = self._repo.find_by_id(source_id)
        if existing is None:
            raise EntityNotFoundError("Fonte de scraping", str(source_id))

        self._repo.delete(source_id)
        self._logs.create(
            user_id=actor_id,
            action=AccessAction.CONFIG_UPDATED,
            metadata={"type": "scraping_source", "action": "deleted", "code": existing.code},
        )
        return {"message": "Fonte removida", "code": existing.code}
