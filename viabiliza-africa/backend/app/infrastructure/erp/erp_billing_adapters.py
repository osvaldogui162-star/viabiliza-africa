"""Adaptadores ERP/facturação — APIs abertas e export AGT (sem dependências pagas)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import uuid4


class ErpBillingAdapterError(Exception):
    pass


def _http_json(
    url: str,
    *,
    method: str = "GET",
    payload: dict | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 25.0,
) -> Any:
    data = None
    hdrs = {"Content-Type": "application/json", **(headers or {})}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            if not body:
                return {}
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise ErpBillingAdapterError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ErpBillingAdapterError(str(exc)) from exc


def test_connection(provider_code: str, config: dict[str, Any]) -> None:
    code = provider_code.strip().lower()
    if code == "odoo":
        _odoo_version(config)
    elif code == "zoho_books":
        _zoho_ping(config)
    elif code in ("primavera_erp", "fact_flexi", "novabilling"):
        base = (config.get("base_url") or "").rstrip("/")
        if not base:
            raise ErpBillingAdapterError("base_url em falta")
        _http_json(f"{base}/health", method="GET", headers=_api_headers(config))
    elif code == "generic_webhook":
        url = config.get("webhook_url")
        if not url:
            raise ErpBillingAdapterError("webhook_url em falta")
        _http_json(
            url,
            method="POST",
            payload={"event": "connection_test", "source": "viabiliza_africa"},
            headers=_webhook_headers(config),
        )
    elif code == "agt_export":
        if not config.get("taxpayer_nif"):
            raise ErpBillingAdapterError("NIF do contribuinte em falta")
    else:
        raise ErpBillingAdapterError(f"Fornecedor desconhecido: {provider_code}")


def issue_subscription_invoice(
    provider_code: str,
    config: dict[str, Any],
    *,
    invoice: dict[str, Any],
) -> dict[str, Any]:
    """Emite ou regista documento fiscal de assinatura. Retorna external_ref e payload."""
    code = provider_code.strip().lower()
    if code == "odoo":
        return _odoo_create_invoice(config, invoice)
    if code == "zoho_books":
        return _zoho_create_invoice(config, invoice)
    if code in ("primavera_erp", "fact_flexi", "novabilling"):
        return _rest_create_invoice(config, invoice, path="/invoices")
    if code == "generic_webhook":
        return _webhook_invoice(config, invoice)
    if code == "agt_export":
        return _agt_export_invoice(config, invoice)
    raise ErpBillingAdapterError(f"Fornecedor desconhecido: {provider_code}")


def _api_headers(config: dict[str, Any]) -> dict[str, str]:
    key = config.get("api_key") or config.get("auth_token")
    if not key:
        return {}
    return {"Authorization": f"Bearer {key}"}


def _webhook_headers(config: dict[str, Any]) -> dict[str, str]:
    raw = config.get("auth_header")
    if not raw:
        return {}
    if raw.lower().startswith("bearer ") or raw.lower().startswith("basic "):
        return {"Authorization": raw}
    return {"Authorization": f"Bearer {raw}"}


def _odoo_jsonrpc(config: dict[str, Any], service: str, method: str, args: list) -> Any:
    base = (config.get("base_url") or "").rstrip("/")
    db = config.get("database")
    user = config.get("username")
    api_key = config.get("api_key")
    if not all([base, db, user, api_key]):
        raise ErpBillingAdapterError("Configuração Odoo incompleta")
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {"service": service, "method": method, "args": args},
        "id": 1,
    }
    result = _http_json(f"{base}/jsonrpc", method="POST", payload=payload)
    if result.get("error"):
        raise ErpBillingAdapterError(str(result["error"]))
    return result.get("result")


def _odoo_version(config: dict[str, Any]) -> None:
    _odoo_jsonrpc(config, "common", "version", [])


def _odoo_create_invoice(config: dict[str, Any], invoice: dict[str, Any]) -> dict[str, Any]:
    uid = _odoo_jsonrpc(
        config,
        "common",
        "authenticate",
        [config["database"], config["username"], config["api_key"], {}],
    )
    if not uid:
        raise ErpBillingAdapterError("Autenticação Odoo falhou")
    partner_name = invoice.get("customer_name") or "Cliente ViabilizA+"
    line_name = invoice.get("description") or "Assinatura ViabilizA+"
    amount = float(invoice.get("amount") or 0)
    move_vals = {
        "move_type": "out_invoice",
        "partner_id": False,
        "invoice_line_ids": [
            (
                0,
                0,
                {
                    "name": line_name,
                    "quantity": 1,
                    "price_unit": amount,
                },
            )
        ],
        "ref": invoice.get("reference"),
        "narration": f"Parceiro: {partner_name}",
    }
    move_id = _odoo_jsonrpc(
        config,
        "object",
        "execute_kw",
        [
            config["database"],
            uid,
            config["api_key"],
            "account.move",
            "create",
            [move_vals],
        ],
    )
    return {
        "external_ref": str(move_id),
        "document_payload": {"odoo_move_id": move_id, "partner_name": partner_name},
    }


def _zoho_ping(config: dict[str, Any]) -> None:
    org = config.get("organization_id")
    domain = (config.get("api_domain") or "https://www.zohoapis.com").rstrip("/")
    token = config.get("auth_token")
    if not org or not token:
        raise ErpBillingAdapterError("organization_id e auth_token são obrigatórios")
    _http_json(
        f"{domain}/books/v3/organizations/{org}",
        headers={"Authorization": f"Zoho-oauthtoken {token}"},
    )


def _zoho_create_invoice(config: dict[str, Any], invoice: dict[str, Any]) -> dict[str, Any]:
    org = config["organization_id"]
    domain = (config.get("api_domain") or "https://www.zohoapis.com").rstrip("/")
    token = config["auth_token"]
    body = {
        "customer_name": invoice.get("customer_name") or "Cliente",
        "line_items": [
            {
                "name": invoice.get("description") or "Assinatura",
                "rate": float(invoice.get("amount") or 0),
                "quantity": 1,
            }
        ],
        "reference_number": invoice.get("reference"),
    }
    result = _http_json(
        f"{domain}/books/v3/invoices?organization_id={org}",
        method="POST",
        payload=body,
        headers={"Authorization": f"Zoho-oauthtoken {token}"},
    )
    inv = (result.get("invoice") or {}) if isinstance(result, dict) else {}
    return {
        "external_ref": str(inv.get("invoice_id") or inv.get("invoice_number") or uuid4()),
        "document_payload": result if isinstance(result, dict) else {"raw": result},
    }


def _rest_create_invoice(config: dict[str, Any], invoice: dict[str, Any], *, path: str) -> dict[str, Any]:
    base = config["base_url"].rstrip("/")
    result = _http_json(
        f"{base}{path}",
        method="POST",
        payload={
            "reference": invoice.get("reference"),
            "amount": float(invoice.get("amount") or 0),
            "currency": invoice.get("currency") or "AOA",
            "description": invoice.get("description"),
            "customer": {"name": invoice.get("customer_name"), "email": invoice.get("customer_email")},
        },
        headers=_api_headers(config),
    )
    ext = None
    if isinstance(result, dict):
        ext = result.get("id") or result.get("invoice_id") or result.get("number")
    return {
        "external_ref": str(ext or uuid4()),
        "document_payload": result if isinstance(result, dict) else {"raw": result},
    }


def _webhook_invoice(config: dict[str, Any], invoice: dict[str, Any]) -> dict[str, Any]:
    url = config["webhook_url"]
    result = _http_json(
        url,
        method="POST",
        payload={"event": "subscription_invoice", "invoice": invoice},
        headers=_webhook_headers(config),
    )
    ext = None
    if isinstance(result, dict):
        ext = result.get("external_ref") or result.get("id")
    return {
        "external_ref": str(ext or uuid4()),
        "document_payload": result if isinstance(result, dict) else {"raw": result},
    }


def _agt_export_invoice(config: dict[str, Any], invoice: dict[str, Any]) -> dict[str, Any]:
    nif = str(config.get("taxpayer_nif") or "").strip()
    cert_id = config.get("software_certificate_id") or "VIABILIZA-PLUS"
    doc_id = str(uuid4())
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    amount = Decimal(str(invoice.get("amount") or "0"))
    root = ET.Element("AgtEInvoiceExport", attrib={"version": "1.0", "xmlns": "urn:viabiliza:agt:export"})
    ET.SubElement(root, "SoftwareCertificateId").text = str(cert_id)
    ET.SubElement(root, "TaxpayerNIF").text = nif
    ET.SubElement(root, "DocumentId").text = doc_id
    ET.SubElement(root, "IssueDateTime").text = now
    ET.SubElement(root, "Currency").text = str(invoice.get("currency") or "AOA")
    ET.SubElement(root, "NetAmount").text = f"{amount:.2f}"
    ET.SubElement(root, "TaxAmount").text = "0.00"
    ET.SubElement(root, "GrossAmount").text = f"{amount:.2f}"
    ET.SubElement(root, "Description").text = str(invoice.get("description") or "Assinatura ViabilizA+")
    ET.SubElement(root, "PaymentReference").text = str(invoice.get("reference") or "")
    xml = ET.tostring(root, encoding="unicode", xml_declaration=True)
    return {
        "external_ref": doc_id,
        "document_payload": {
            "format": "agt_export_v1",
            "taxpayer_nif": nif,
            "payment_reference": invoice.get("reference"),
        },
        "agt_export_xml": xml,
        "status_hint": "export_ready",
    }
