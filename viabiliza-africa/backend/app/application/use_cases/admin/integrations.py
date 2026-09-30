from uuid import UUID

import requests

from app.application.services.admin_access_policy import AdminAccessPolicy
from app.application.services.integration_config_service import IntegrationConfigService
from app.application.use_cases.admin.mappers import to_integration_output
from app.domain.enums.access_action import AccessAction
from app.domain.enums.integration_key import IntegrationKey
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, ValidationError
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.admin_config_repository import IIntegrationSettingsRepository


class ListIntegrationsUseCase:
    """UC36 — Listar integrações configuradas."""

    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: IIntegrationSettingsRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository

    def execute(self, *, actor_id: UUID) -> dict:
        self._policy.require_admin(actor_id)
        items = self._repo.find_all()
        return {
            "items": [to_integration_output(i, masked=True) for i in items],
            "total": len(items),
        }


class GetIntegrationUseCase:
    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: IIntegrationSettingsRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository

    def execute(self, *, actor_id: UUID, integration_key: str) -> dict:
        self._policy.require_admin(actor_id)
        if not IntegrationKey.is_valid(integration_key):
            raise ValidationError(f"Integração inválida: {integration_key}")
        row = self._repo.find_by_key(IntegrationKey(integration_key))
        if row is None:
            raise EntityNotFoundError("Integração", integration_key)
        return to_integration_output(row, masked=True)


class UpdateIntegrationUseCase:
    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        repository: IIntegrationSettingsRepository,
        config_service: IntegrationConfigService,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._policy = admin_policy
        self._repo = repository
        self._config = config_service
        self._logs = access_log_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        integration_key: str,
        settings: dict,
        is_active: bool = True,
    ) -> dict:
        self._policy.require_admin(actor_id)
        if not IntegrationKey.is_valid(integration_key):
            raise ValidationError(f"Integração inválida: {integration_key}")

        key = IntegrationKey(integration_key)
        existing = self._repo.find_by_key(key)
        merged = dict(existing.settings) if existing else {}
        for k, v in settings.items():
            if v is not None and v != "":
                merged[k] = v

        row = self._repo.upsert(key, settings=merged, is_active=is_active, updated_by=actor_id)
        self._config.invalidate_cache()

        self._logs.create(
            user_id=actor_id,
            action=AccessAction.CONFIG_UPDATED,
            metadata={"type": "integration", "key": integration_key},
        )
        return to_integration_output(row, masked=True)


class TestIntegrationUseCase:
    """Testa ligação às APIs bancárias."""

    def __init__(
        self,
        admin_policy: AdminAccessPolicy,
        config_service: IntegrationConfigService,
    ) -> None:
        self._policy = admin_policy
        self._config = config_service

    def execute(self, *, actor_id: UUID, integration_key: str) -> dict:
        self._policy.require_admin(actor_id)
        if integration_key not in (IntegrationKey.BFA.value, IntegrationKey.BDA.value):
            raise ValidationError("Teste disponível apenas para integrações BFA e BDA")

        key = IntegrationKey(integration_key)
        if key == IntegrationKey.BFA:
            url, api_key = self._config.get_bfa_config()
        else:
            url, api_key = self._config.get_bda_config()

        if not url:
            return {
                "success": False,
                "message": f"API {integration_key.upper()} não configurada — usando modo simulação",
            }

        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = requests.get(url.rstrip("/") + "/health", headers=headers, timeout=10)
            ok = response.status_code < 500
            return {
                "success": ok,
                "status_code": response.status_code,
                "message": "Ligação OK" if ok else f"Resposta inesperada: {response.status_code}",
            }
        except requests.RequestException as exc:
            return {"success": False, "message": f"Falha na ligação: {exc}"}
