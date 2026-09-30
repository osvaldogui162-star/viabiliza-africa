"""Cliente HTTP AppyPay — ambiente TST."""

from __future__ import annotations

import re
import time
import uuid
from decimal import Decimal
from typing import Any

import requests

from app.config import Config


SANDBOX_GPO_PHONES_META = [
    {
        "number": "244900000000",
        "label": "Sucesso",
        "description": "Pagamento aprovado automaticamente (sandbox)",
    },
    {
        "number": "244900000001",
        "label": "Saldo insuficiente",
        "description": "Simula recusa por saldo",
    },
    {
        "number": "244900000002",
        "label": "Timeout",
        "description": "Simula timeout do processador",
    },
    {
        "number": "244900000003",
        "label": "Rejeitado",
        "description": "Simula rejeição pelo cliente",
    },
]


SANDBOX_GPO_PHONES = frozenset(item["number"] for item in SANDBOX_GPO_PHONES_META)


def appypay_checkout_meta(*, sandbox: bool) -> dict:
    return {
        "sandbox": sandbox,
        "sandbox_gpo_phones": SANDBOX_GPO_PHONES_META,
        "gpo_note": (
            "No TST, números reais não recebem push no Multicaixa Express. "
            "Use os números de teste AppyPay."
            if sandbox
            else None
        ),
    }


class AppyPayError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None, payload: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload


class AppyPayClient:
    TOKEN_URL = "https://login.microsoftonline.com/appypaydev.onmicrosoft.com/oauth2/token"

    def __init__(self, config: Config) -> None:
        self._client_id = config.APPYPAY_CLIENT_ID
        self._client_secret = config.APPYPAY_CLIENT_SECRET
        self._resource = config.APPYPAY_RESOURCE
        self._gpo_method = config.APPYPAY_GPO_METHOD
        self._ref_method = config.APPYPAY_REF_METHOD
        self._api_base = config.APPYPAY_API_BASE.rstrip("/")
        self._token: str | None = None
        self._token_expires_at: float = 0.0

    def _ensure_configured(self) -> None:
        if not self._client_id or not self._client_secret or not self._resource:
            raise AppyPayError("AppyPay não configurado — defina APPYPAY_CLIENT_ID/SECRET/RESOURCE")

    def get_access_token(self, *, force_refresh: bool = False) -> str:
        self._ensure_configured()
        if not force_refresh and self._token and time.time() < self._token_expires_at - 60:
            return self._token

        response = requests.post(
            self.TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "resource": self._resource,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )
        if response.status_code >= 400:
            raise AppyPayError(
                "Falha na autenticação AppyPay",
                status_code=response.status_code,
                payload=_safe_json(response),
            )

        data = response.json()
        token = data.get("access_token")
        if not token:
            raise AppyPayError("Resposta AppyPay sem access_token", payload=data)

        expires_in = int(data.get("expires_in", 3600))
        self._token = token
        self._token_expires_at = time.time() + expires_in
        return token

    def create_gpo_charge(
        self,
        *,
        amount: Decimal,
        phone_number: str,
        merchant_transaction_id: str,
        description: str,
    ) -> dict[str, Any]:
        return self._create_charge(
            amount=amount,
            merchant_transaction_id=merchant_transaction_id,
            description=description,
            payment_method=self._gpo_method,
            payment_info={"phoneNumber": _normalize_phone(phone_number)},
        )

    def create_ref_charge(
        self,
        *,
        amount: Decimal,
        merchant_transaction_id: str,
        description: str,
    ) -> dict[str, Any]:
        return self._create_charge(
            amount=amount,
            merchant_transaction_id=merchant_transaction_id,
            description=description,
            payment_method=self._ref_method,
        )

    def get_charge(self, charge_id: str) -> dict[str, Any]:
        token = self.get_access_token()
        url = f"{self._api_base}/charges/{charge_id}"
        response = self._request_get(url, token)
        if response.status_code == 401:
            response = self._request_get(url, self.get_access_token(force_refresh=True))
        if response.status_code >= 400:
            raise AppyPayError(
                "Falha ao consultar cobrança AppyPay",
                status_code=response.status_code,
                payload=_safe_json(response),
            )
        return response.json()

    def mock_reference_payment(self, *, entity: str, reference_number: str) -> dict[str, Any]:
        token = self.get_access_token()
        response = requests.post(
            f"{self._api_base}/mocks/referenceProcessing",
            json={"entity": entity, "referenceNumber": reference_number},
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            timeout=30,
        )
        if response.status_code >= 400:
            raise AppyPayError(
                "Falha ao simular pagamento por referência (sandbox)",
                status_code=response.status_code,
                payload=_safe_json(response),
            )
        return response.json() if response.text else {"ok": True}

    def _create_charge(
        self,
        *,
        amount: Decimal,
        merchant_transaction_id: str,
        description: str,
        payment_method: str,
        payment_info: dict | None = None,
    ) -> dict[str, Any]:
        token = self.get_access_token()
        payload: dict[str, Any] = {
            "amount": float(amount),
            "currency": "AOA",
            "description": description[:200],
            "merchantTransactionId": merchant_transaction_id,
            "paymentMethod": payment_method,
        }
        if payment_info:
            payload["paymentInfo"] = payment_info

        response = requests.post(
            f"{self._api_base}/charges",
            json=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            timeout=45,
        )
        if response.status_code == 401:
            token = self.get_access_token(force_refresh=True)
            response = requests.post(
                f"{self._api_base}/charges",
                json=payload,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
                timeout=45,
            )
        if response.status_code >= 400:
            raise AppyPayError(
                "AppyPay recusou a criação da cobrança",
                status_code=response.status_code,
                payload=_safe_json(response),
            )
        return response.json()

    @staticmethod
    def _request_get(url: str, token: str) -> requests.Response:
        return requests.get(
            url,
            headers={"Accept": "application/json", "Authorization": f"Bearer {token}"},
            timeout=30,
        )

    @staticmethod
    def new_merchant_transaction_id() -> str:
        # AppyPay: máx. 15 caracteres alfanuméricos (a-z, A-Z, 0-9)
        return uuid.uuid4().hex[:15].upper()


def _safe_json(response: requests.Response) -> Any:
    try:
        return response.json()
    except Exception:
        return {"text": response.text[:500]}


def _normalize_phone(phone: str) -> str:
    digits = "".join(ch for ch in phone if ch.isdigit())
    if digits.startswith("244"):
        return digits
    if digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 9:
        return f"244{digits}"
    return digits


def is_sandbox_gpo_phone(phone: str) -> bool:
    return _normalize_phone(phone) in SANDBOX_GPO_PHONES


def extract_error_message(response: dict[str, Any]) -> str | None:
    response_status = response.get("responseStatus")
    if isinstance(response_status, dict):
        if response_status.get("successful") is True:
            return None
        parts: list[str] = []
        message = response_status.get("message")
        if message:
            parts.append(str(message).strip())
        source_details = response_status.get("sourceDetails")
        if isinstance(source_details, dict):
            detail_message = source_details.get("message")
            detail_code = source_details.get("code")
            if detail_message:
                cleaned = _clean_appypay_text(str(detail_message))
                if cleaned and cleaned not in parts:
                    parts.append(cleaned)
            if detail_code and detail_code not in {"NONE", "OK"}:
                code_text = str(detail_code)
                if not any(code_text in part for part in parts):
                    parts.append(f"Código: {code_text}")
        if parts:
            return " ".join(parts)

    payment = response.get("payment")
    if isinstance(payment, dict):
        events = payment.get("transactionEvents") or []
        for event in reversed(events):
            event_status = event.get("responseStatus")
            if isinstance(event_status, dict) and event_status.get("successful") is False:
                message = event_status.get("message")
                if message:
                    return str(message).strip()
    return None


def _clean_appypay_text(value: str) -> str:
    text = value.replace("\u00c3\u00a1", "á").replace("\u00c3\u00b3", "ó").replace("\u00c3\u00a9", "é")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def map_appypay_status(raw_status: str | None) -> str:
    if not raw_status:
        return "pending"
    normalized = raw_status.strip().lower()
    success = {"paid", "success", "successful", "completed", "approved", "accepted", "confirmed"}
    failed = {"failed", "declined", "rejected", "error", "cancelled", "canceled", "expired"}
    pending = {"pending", "processing", "inprogress", "in_progress", "awaiting", "waiting"}
    if normalized in success:
        return "paid"
    if normalized in failed:
        return "failed"
    if normalized in pending:
        return "processing"
    return "processing"


def extract_charge_id(response: dict[str, Any]) -> str | None:
    payment = response.get("payment")
    if isinstance(payment, dict) and payment.get("id"):
        return str(payment["id"])
    for key in ("id", "chargeId", "charge_id"):
        if response.get(key):
            return str(response[key])
    data = response.get("data")
    if isinstance(data, dict):
        for key in ("id", "chargeId", "charge_id"):
            if data.get(key):
                return str(data[key])
    return None


def extract_reference(response: dict[str, Any]) -> tuple[str | None, str | None]:
    candidates: list[dict[str, Any]] = []
    payment = response.get("payment")
    if isinstance(payment, dict):
        candidates.append(payment)
        ref_block = payment.get("reference")
        if isinstance(ref_block, dict):
            candidates.append(ref_block)
    candidates.append(response)
    response_status = response.get("responseStatus")
    if isinstance(response_status, dict):
        candidates.append(response_status)
        ref_block = response_status.get("reference")
        if isinstance(ref_block, dict):
            candidates.append(ref_block)
    if isinstance(response.get("data"), dict):
        candidates.append(response["data"])
    if isinstance(response.get("paymentInfo"), dict):
        candidates.append(response["paymentInfo"])
    if isinstance(response.get("reference"), dict):
        candidates.append(response["reference"])

    entity = None
    reference = None
    for item in candidates:
        entity = entity or item.get("entity") or item.get("referenceEntity")
        reference = reference or item.get("referenceNumber") or item.get("reference_number")
        ref_value = item.get("reference")
        if isinstance(ref_value, dict):
            entity = entity or ref_value.get("entity")
            reference = reference or ref_value.get("referenceNumber")
        elif isinstance(ref_value, str):
            reference = reference or ref_value
    return (
        str(entity) if entity else None,
        str(reference) if reference else None,
    )


def extract_status(response: dict[str, Any]) -> str | None:
    payment = response.get("payment")
    if isinstance(payment, dict):
        for key in ("status", "chargeStatus", "paymentStatus"):
            if payment.get(key):
                return str(payment[key])
    for key in ("status", "chargeStatus", "paymentStatus"):
        if response.get(key):
            return str(response[key])
    response_status = response.get("responseStatus")
    if isinstance(response_status, dict):
        for key in ("status", "chargeStatus", "paymentStatus"):
            if response_status.get(key):
                return str(response_status[key])
    data = response.get("data")
    if isinstance(data, dict):
        for key in ("status", "chargeStatus", "paymentStatus"):
            if data.get(key):
                return str(data[key])
    return None
