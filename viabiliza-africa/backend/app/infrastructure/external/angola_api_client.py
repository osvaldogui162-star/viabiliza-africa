"""Cliente HTTP para Angola API (validações nacionais)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from urllib.parse import quote

import requests

from app.domain.validators.angola_national import (
    validate_bi_format,
    validate_local_phone,
    to_international_phone,
)

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://angolaapi.onrender.com/api/v1"


@dataclass(frozen=True)
class AngolaValidationResult:
    valid: bool
    message: str
    source: str  # angola_api | local
    operator: str | None = None
    normalized_value: str | None = None


class AngolaApiClient:
    """Integração com Angola API para validação de BI e telefone."""

    def __init__(self, *, base_url: str = DEFAULT_BASE_URL, timeout: int = 10) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def validate_bi(self, bi: str) -> AngolaValidationResult:
        # Formato oficial Angola API: /^\d{9}[A-Za-z]{2}\d{3}$/
        normalized = validate_bi_format(bi)

        remote = self._request_validate(f"validate/bi/{quote(normalized, safe='')}")
        if remote is not None and remote.valid:
            return AngolaValidationResult(
                valid=True,
                message=remote.message,
                source="angola_api",
                normalized_value=normalized,
            )

        # Formato local alinhado com Angola-Api validateBi.ts
        return AngolaValidationResult(
            valid=True,
            message="Número de BI com formato nacional válido",
            source="local",
            normalized_value=normalized,
        )

    def validate_phone(self, phone: str, *, optional: bool = False) -> AngolaValidationResult:
        if not phone or not str(phone).strip():
            if optional:
                return AngolaValidationResult(
                    valid=True,
                    message="Contacto não informado",
                    source="local",
                    normalized_value=None,
                )
            raise ValueError("Contacto é obrigatório")

        # Regra de negócio: exactamente 9 dígitos, só números, começa por 9
        normalized = validate_local_phone(phone)
        international = to_international_phone(normalized)

        remote = self._request_validate(f"validate/phone/{quote(international, safe='')}")
        if remote is not None and remote.valid:
            return AngolaValidationResult(
                valid=True,
                message=remote.message,
                source="angola_api",
                operator=remote.operator,
                normalized_value=normalized,
            )

        return AngolaValidationResult(
            valid=True,
            message="Número de telefone angolano válido",
            source="local",
            normalized_value=normalized,
        )

    def _request_validate(self, path: str) -> AngolaValidationResult | None:
        url = f"{self._base_url}/{path.lstrip('/')}"
        try:
            response = requests.get(
                url,
                timeout=self._timeout,
                headers={"Accept": "application/json", "User-Agent": "ViabilizA+Africa/1.0"},
            )
            payload = {}
            try:
                payload = response.json() if response.content else {}
            except ValueError:
                payload = {}

            if response.status_code == 200:
                message = str(payload.get("message") or "Validação concluída com sucesso")
                return AngolaValidationResult(
                    valid=True,
                    message=message,
                    source="angola_api",
                    operator=payload.get("operator"),
                )

            if response.status_code == 400:
                message = str(payload.get("message") or "Dado inválido")
                return AngolaValidationResult(
                    valid=False,
                    message=message,
                    source="angola_api",
                )

            logger.warning("Angola API respondeu %s para %s", response.status_code, url)
            return None
        except requests.RequestException as exc:
            logger.warning("Angola API indisponível (%s): %s", url, exc)
            return None
