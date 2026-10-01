"""Catálogo de ERP/facturação — Angola e África (APIs abertas / integração documentada)."""

from __future__ import annotations

from typing import Any

# Regiões: AO = Angola, SADC, PAN = multi-país África
ERP_BILLING_PROVIDERS: tuple[dict[str, Any], ...] = (
    {
        "code": "odoo",
        "name": "Odoo",
        "regions": ["AO", "SADC", "PAN"],
        "integration": "openapi",
        "api_style": "json_rpc",
        "agt_certified": False,
        "free_tier": True,
        "notes_pt": "API aberta; ideal para PME com instância própria ou Odoo.com.",
        "notes_en": "Open API; suited for SMEs on self-hosted or Odoo.com.",
        "config_fields": [
            {"key": "base_url", "label_pt": "URL Odoo", "required": True},
            {"key": "database", "label_pt": "Base de dados", "required": True},
            {"key": "username", "label_pt": "Utilizador", "required": True},
            {"key": "api_key", "label_pt": "Chave API / password", "required": True, "secret": True},
        ],
    },
    {
        "code": "zoho_books",
        "name": "Zoho Books",
        "regions": ["PAN"],
        "integration": "rest_oauth",
        "api_style": "rest",
        "agt_certified": False,
        "free_tier": True,
        "notes_pt": "API REST; plano gratuito limitado — verificar conformidade AGT.",
        "notes_en": "REST API; limited free tier — check AGT compliance.",
        "config_fields": [
            {"key": "organization_id", "label_pt": "Organization ID", "required": True},
            {"key": "auth_token", "label_pt": "Token OAuth / Zoho-oauthtoken", "required": True, "secret": True},
            {"key": "api_domain", "label_pt": "Domínio API", "required": False, "default": "https://www.zohoapis.com"},
        ],
    },
    {
        "code": "primavera_erp",
        "name": "Primavera ERP (Cegid)",
        "regions": ["AO", "SADC"],
        "integration": "rest",
        "api_style": "rest",
        "agt_certified": True,
        "free_tier": False,
        "notes_pt": "Certificado AGT; requer licença e endpoints do parceiro.",
        "notes_en": "AGT certified; requires license and partner endpoints.",
        "config_fields": [
            {"key": "base_url", "label_pt": "URL API Primavera", "required": True},
            {"key": "api_key", "label_pt": "Chave API", "required": True, "secret": True},
            {"key": "company_code", "label_pt": "Código empresa", "required": True},
        ],
    },
    {
        "code": "fact_flexi",
        "name": "Fact Flexi",
        "regions": ["AO"],
        "integration": "rest",
        "api_style": "rest",
        "agt_certified": True,
        "free_tier": True,
        "notes_pt": "ERP angolano; integração API/WhatsApp conforme fornecedor.",
        "notes_en": "Angolan ERP; API/WhatsApp per vendor docs.",
        "config_fields": [
            {"key": "base_url", "label_pt": "URL API", "required": True},
            {"key": "api_key", "label_pt": "Chave API", "required": True, "secret": True},
        ],
    },
    {
        "code": "novabilling",
        "name": "NovaBilling (API aberta)",
        "regions": ["PAN"],
        "integration": "rest",
        "api_style": "rest",
        "agt_certified": False,
        "free_tier": True,
        "notes_pt": "Billing pan-africano; gateways Paystack, Flutterwave, etc.",
        "notes_en": "Pan-African billing; Paystack, Flutterwave gateways.",
        "config_fields": [
            {"key": "base_url", "label_pt": "URL API", "required": True},
            {"key": "api_key", "label_pt": "Chave API", "required": True, "secret": True},
        ],
    },
    {
        "code": "generic_webhook",
        "name": "Webhook genérico (ERP próprio)",
        "regions": ["AO", "SADC", "PAN"],
        "integration": "webhook",
        "api_style": "webhook",
        "agt_certified": False,
        "free_tier": True,
        "notes_pt": "POST JSON para o seu ERP (SAP B1, NetSuite, etc.).",
        "notes_en": "POST JSON to your ERP (SAP B1, NetSuite, etc.).",
        "config_fields": [
            {"key": "webhook_url", "label_pt": "URL webhook", "required": True},
            {"key": "auth_header", "label_pt": "Header Authorization (opcional)", "required": False, "secret": True},
        ],
    },
    {
        "code": "agt_export",
        "name": "Export AGT (sem API externa)",
        "regions": ["AO"],
        "integration": "local_export",
        "api_style": "none",
        "agt_certified": True,
        "free_tier": True,
        "notes_pt": "Gera pacote estruturado para submissão manual/portal AGT.",
        "notes_en": "Structured export for manual AGT portal submission.",
        "config_fields": [
            {"key": "taxpayer_nif", "label_pt": "NIF do contribuinte", "required": True},
            {"key": "software_certificate_id", "label_pt": "ID certificação software (opcional)", "required": False},
        ],
    },
)


def get_provider(code: str) -> dict[str, Any] | None:
    key = (code or "").strip().lower()
    for p in ERP_BILLING_PROVIDERS:
        if p["code"] == key:
            return p
    return None


def list_providers_public() -> list[dict[str, Any]]:
    """Metadados seguros para UI (sem segredos)."""
    out: list[dict[str, Any]] = []
    for p in ERP_BILLING_PROVIDERS:
        out.append(
            {
                "code": p["code"],
                "name": p["name"],
                "regions": p["regions"],
                "integration": p["integration"],
                "agt_certified": p["agt_certified"],
                "free_tier": p["free_tier"],
                "notes_pt": p["notes_pt"],
                "notes_en": p["notes_en"],
                "config_fields": p["config_fields"],
            }
        )
    return out
