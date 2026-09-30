import logging
import uuid

import requests

from app.application.services.integration_config_service import IntegrationConfigService
from app.config import Config
from app.domain.enums.bank_code import BankCode
from app.domain.exceptions.domain_exceptions import ValidationError

logger = logging.getLogger(__name__)


class BankApiClient:
    """Cliente para submissão de relatórios a BFA/BDA (UC34)."""

    def __init__(
        self,
        config: Config,
        integration_config: IntegrationConfigService | None = None,
    ) -> None:
        self._config = config
        self._integration = integration_config

    def submit(
        self,
        bank: BankCode,
        *,
        project_payload: dict,
        report_hash: str,
        pdf_size: int,
    ) -> dict:
        url = self._endpoint(bank)
        if not url:
            ref = f"SIM-{bank.value.upper()}-{uuid.uuid4().hex[:12].upper()}"
            logger.info("API %s não configurada — submissão simulada: %s", bank.value, ref)
            return {
                "status": "submitted",
                "external_ref": ref,
                "message": f"Submissão simulada para {bank.value.upper()} (configure API no .env)",
            }

        payload = {
            "project": project_payload,
            "report_verification_hash": report_hash,
            "document_size_bytes": pdf_size,
        }
        headers = {"Content-Type": "application/json"}
        api_key = self._api_key(bank)
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            if not response.ok:
                raise ValidationError(
                    f"Erro API {bank.value.upper()} ({response.status_code}): {response.text[:200]}"
                )
            data = response.json()
            return {
                "status": data.get("status", "submitted"),
                "external_ref": data.get("reference") or data.get("id"),
                "message": data.get("message", "Submetido com sucesso"),
                "raw": data,
            }
        except requests.RequestException as exc:
            raise ValidationError(f"Falha na ligação à API {bank.value.upper()}: {exc}") from exc

    def _endpoint(self, bank: BankCode) -> str:
        if self._integration:
            if bank == BankCode.BFA:
                url, _ = self._integration.get_bfa_config()
                return url
            url, _ = self._integration.get_bda_config()
            return url
        if bank == BankCode.BFA:
            return self._config.BFA_API_URL
        return self._config.BDA_API_URL

    def _api_key(self, bank: BankCode) -> str:
        if self._integration:
            if bank == BankCode.BFA:
                _, key = self._integration.get_bfa_config()
                return key
            _, key = self._integration.get_bda_config()
            return key
        if bank == BankCode.BFA:
            return self._config.BFA_API_KEY
        return self._config.BDA_API_KEY
