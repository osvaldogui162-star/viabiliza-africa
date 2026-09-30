"""Contactos da fonte real de cada preço automático (portais oficiais + retalho)."""

from __future__ import annotations

import logging
import re
import threading
from dataclasses import dataclass

from app.domain.catalog.angolan_retail_suppliers import (
    codes_for_catalog_category,
    suppliers_by_code,
)
from app.domain.entities.cost_item import CostItem
from app.infrastructure.scraping.http_utils import fetch_html_first

logger = logging.getLogger(__name__)

_CACHE: dict[str, "SupplierContact"] = {}
_CACHE_LOCK = threading.Lock()


@dataclass(frozen=True)
class SupplierContact:
    code: str
    name: str
    email: str | None
    phone: str | None
    portal_url: str | None
    contact_page: str | None = None


# Instituições / portais oficiais usados nas referências setoriais + retalho
KNOWN_CONTACTS: dict[str, dict[str, str | None]] = {
    # --- Fontes institucionais (referência setorial) ---
    "agt": {
        "name": "AGT — Administração Geral Tributária",
        "email": "apoio.agt@minfin.gov.ao",
        "phone": "+244 923 167 010",
        "portal_url": "https://agt.minfin.gov.ao",
        "contact_page": "https://portaldocontribuinte.minfin.gov.ao/contactos",
    },
    "gue": {
        "name": "GUE — Guiché Único da Empresa",
        "email": "gue@gue.gov.ao",
        "phone": "+244 222 760 681",
        "portal_url": "https://gue.gov.ao",
        "contact_page": "https://gue.gov.ao/",
    },
    "maptss": {
        "name": "MAPTSS — Trabalho e Segurança Social",
        "email": "contacto@maptss.gov.ao",
        "phone": None,
        "portal_url": "https://www.maptss.gov.ao",
        "contact_page": "https://www.maptss.gov.ao/",
    },
    "minfin": {
        "name": "Portal do Contribuinte (MINFIN)",
        "email": "portaldocontribuinte@minfin.gov.ao",
        "phone": "+244 923 167 010",
        "portal_url": "https://portaldocontribuinte.minfin.gov.ao",
        "contact_page": "https://portaldocontribuinte.minfin.gov.ao/contactos",
    },
    "minagrif": {
        "name": "MINAGRIF — Agricultura e Florestas",
        "email": "geral@minagrif.gov.ao",
        "phone": None,
        "portal_url": "https://www.minagrif.gov.ao",
        "contact_page": "https://www.minagrif.gov.ao/",
    },
    "ocea": {
        "name": "Ordem dos Engenheiros de Angola",
        "email": "secretaria@oea.org.ao",
        "phone": None,
        "portal_url": "https://www.oea.org.ao",
        "contact_page": "https://www.oea.org.ao/",
    },
    "ocpca": {
        "name": "Ordem dos Contabilistas e Peritos Contabilistas de Angola",
        "email": "geral@ocpca.ao",
        "phone": None,
        "portal_url": "https://www.ocpca.ao",
        "contact_page": "https://www.ocpca.ao/",
    },
    # --- Retalho / marketplaces ---
    "ovarmat": {
        "email": "geral@ovarmatangola.com",
        "phone": "+244 921 180 132",
        "contact_page": "https://www.ovarmatangola.com/pt/faqs",
    },
    "siluz": {
        "email": "sede@siluzangola.com",
        "phone": "+244 938 254 304",
        "contact_page": "https://siluzangola.com/contactos/",
    },
    "moviflor": {
        "email": "loja.morrobento@moviflor.ao",
        "phone": "+244 941 253 703",
        "contact_page": "https://moviflor.ao/contactos/",
    },
    "bricomat": {
        "email": "geral@bricomat.com",
        "phone": "+244 928 189 065",
        "contact_page": "https://bricomat.com/",
    },
    "maxi": {
        "email": "maxi.luanda@maxi.co.ao",
        "phone": "+244 222 013 145",
        "contact_page": "https://www.maxi.co.ao/contactos/lojas/",
    },
    "shoprite": {
        "email": "customercare@shoprite.co.ao",
        "phone": None,
        "contact_page": "https://shoprite.co.ao/",
    },
    "toyota_ao": {
        "email": "apoiocliente@cfaomotorsangola.com",
        "phone": None,
        "contact_page": "https://www.cfaomotorsangola.com/",
    },
    "cfao": {
        "email": "apoiocliente@cfaomotorsangola.com",
        "phone": None,
        "contact_page": "https://www.cfaomotorsangola.com/",
    },
    "arreiou": {
        "email": "contactcenter@arreiou.com",
        "phone": None,
        "contact_page": "https://arreiou.com/",
    },
    "ncr": {
        "email": "cliente.online@ncrangola.com",
        "phone": None,
        "contact_page": "https://www.ncrangola.com/",
    },
    "sistec": {
        "email": "geral@sistec.co.ao",
        "phone": "+244225800800",
        "contact_page": "https://loja.sistec.co.ao/",
    },
    "gudesom": {
        "email": None,
        "phone": "+244933608336",
        "contact_page": "https://gudesom.com/",
    },
    "iscotec_music": {
        "email": None,
        "phone": None,
        "contact_page": "https://www.iscotec.co.ao/",
    },
    "vens_music": {
        "email": None,
        "phone": None,
        "contact_page": "https://www.vensmusic.co.ao/",
    },
    "musicomania": {
        "email": None,
        "phone": "+244997024018",
        "contact_page": "https://www.musicomania.co.ao/",
    },
    "king_kong_music": {
        "email": None,
        "phone": None,
        "contact_page": "https://www.kingkongmusic.co.ao/",
    },
    "casa_musica_ao": {
        "email": None,
        "phone": None,
        "contact_page": "https://www.casadamusica.co.ao/",
    },
    "itec": {
        "email": "geral@itec.co.ao",
        "phone": None,
        "contact_page": "https://www.itec.co.ao/",
    },
    "jumia": {
        "email": "hello@jumia.ao",
        "phone": None,
        "contact_page": "https://www.jumia.ao/",
    },
    "jiji": {
        "email": "support@jiji.ao",
        "phone": None,
        "contact_page": "https://jiji.ao/",
    },
    "kikolo": {
        "email": "info@kikoloonline.com",
        "phone": None,
        "contact_page": "https://kikoloonline.com/",
    },
    "socia": {
        "email": "contacto@socia.ao",
        "phone": None,
        "contact_page": "https://socia.ao/",
    },
    "agrolider": {
        "email": "geral@agrolider.co.ao",
        "phone": None,
        "contact_page": "https://www.agrolider.co.ao/",
    },
    "naval": {
        "email": "geral@naval.co.ao",
        "phone": None,
        "contact_page": "https://www.naval.co.ao/",
    },
    "agroshop": {
        "email": "geral@agroshop.co.ao",
        "phone": None,
        "contact_page": "https://www.agroshop.co.ao/",
    },
    "intercal": {
        "email": "geral@intercal.co.ao",
        "phone": None,
        "contact_page": "https://www.intercal.co.ao/",
    },
    "o_index": {
        "email": "geral@o-index.co.ao",
        "phone": None,
        "contact_page": "https://www.o-index.co.ao/",
    },
    "ferro_lundas": {
        "email": "geral@ferrolundas.co.ao",
        "phone": None,
        "contact_page": "https://www.ferrolundas.co.ao/",
    },
    "soletric": {
        "email": "geral@soletric.co.ao",
        "phone": None,
        "contact_page": "https://www.soletric.co.ao/",
    },
    "megatech": {
        "email": "geral@megatech.co.ao",
        "phone": None,
        "contact_page": "https://www.megatech.co.ao/",
    },
}


_EMAIL_RE = re.compile(
    r"(?:mailto:)?([a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,})",
    re.I,
)
_PHONE_RE = re.compile(
    r"(?:\+?244[\s\-.]?)?(?:9\d{2}|2\d{2})[\s\-.]?\d{3}[\s\-.]?\d{3}",
)


def _normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("244") and len(digits) >= 12:
        rest = digits[3:]
        return f"+244 {rest[:3]} {rest[3:6]} {rest[6:9]}"
    if len(digits) == 9:
        return f"+244 {digits[:3]} {digits[3:6]} {digits[6:]}"
    return raw.strip()


def _scrape_portal_contacts(
    portal_url: str, contact_page: str | None = None
) -> tuple[str | None, str | None]:
    urls: list[str] = []
    if contact_page:
        urls.append(contact_page)
    base = portal_url.rstrip("/")
    urls.extend(
        [
            f"{base}/contactos",
            f"{base}/contacto",
            f"{base}/contact",
            f"{base}/contatos",
            f"{base}/pt/contactos",
            base,
        ]
    )
    try:
        html, _ = fetch_html_first(urls[:5], timeout=5)
    except Exception as exc:
        logger.debug("Contact scrape failed for %s: %s", portal_url, exc)
        return None, None

    emails = [
        m.group(1).lower()
        for m in _EMAIL_RE.finditer(html)
        if not any(
            x in m.group(1).lower()
            for x in ("example.", "sentry.", "wixpress", "schema", "png", "jpg")
        )
    ]
    phones = [_normalize_phone(m.group(0)) for m in _PHONE_RE.finditer(html)]
    return (emails[0] if emails else None, phones[0] if phones else None)


def codes_from_reference_context(
    *,
    reference_note: str | None,
    category: str,
    catalog_key: str | None,
    description: str,
) -> list[str]:
    """Mapeia a nota/categoria da referência setorial → portais oficiais da fonte."""
    blob = " ".join(
        filter(None, [reference_note or "", category or "", catalog_key or "", description or ""])
    ).lower()
    codes: list[str] = []

    def add(*items: str) -> None:
        for c in items:
            if c not in codes:
                codes.append(c)

    if any(k in blob for k in ("gue", "licen", "registo", "nif", "agt", "tribut")):
        add("gue", "agt", "minfin")
    if any(k in blob for k in ("contabil", "compliance", "fiscal", "consultoria")):
        add("ocpca", "agt", "minfin")
    if any(k in blob for k in ("agrónomo", "agronomo", "agrícola", "agricola", "minagrif")):
        add("minagrif", "ocea", "naval", "agrolider")
    if any(k in blob for k in ("salário", "salario", "smn", "operário", "operario", "pessoal")):
        add("maptss")
    if any(k in blob for k in ("engenheiro", "honorário", "honorario")):
        add("ocea")
    if category == "Documentação":
        add("gue", "agt")
    if category == "Serviços":
        add("ocpca", "agt")
    if category == "Pessoal" and not codes:
        add("maptss", "ocea")

    # Sempre permitir retalhistas da categoria quando aplicável
    for code in codes_for_catalog_category(category, limit=2):
        add(code)

    return codes[:4]


def get_supplier_contact(code: str, *, scrape_missing: bool = False) -> SupplierContact | None:
    """Contacto da fonte por código (instituição ou retalhista)."""
    with _CACHE_LOCK:
        if code in _CACHE:
            return _CACHE[code]

    retail = suppliers_by_code().get(code)
    known = KNOWN_CONTACTS.get(code, {})
    name = (
        known.get("name")
        or (retail.name if retail else None)
        or code.replace("_", " ").title()
    )
    portal = (
        known.get("portal_url")
        or (retail.base_url if retail else None)
        or known.get("contact_page")
    )
    email = known.get("email")
    phone = known.get("phone")
    contact_page = known.get("contact_page") or (
        f"{str(portal).rstrip('/')}/contactos" if portal else None
    )

    if scrape_missing and portal and (not email or not phone):
        scraped_email, scraped_phone = _scrape_portal_contacts(str(portal), contact_page)
        email = email or scraped_email
        phone = phone or scraped_phone

    if not portal and not email and not phone:
        return None

    contact = SupplierContact(
        code=code,
        name=str(name),
        email=email if isinstance(email, str) else None,
        phone=phone if isinstance(phone, str) else None,
        portal_url=str(portal) if portal else None,
        contact_page=contact_page if isinstance(contact_page, str) else None,
    )
    with _CACHE_LOCK:
        _CACHE[code] = contact
    return contact


def resolve_contacts_for_cost_item(item: CostItem) -> list[dict]:
    """
    Lista contactos da fonte que originou o preço automático:
    1) Marketplace/retalhista exacto (price_source)
    2) Candidatos consultados no scrape (metadata.candidates)
    3) Referência setorial → portais oficiais (AGT, GUE, MAPTSS, …)
    """
    meta = item.metadata or {}
    price_source = meta.get("price_source") or meta.get("scraping_source")
    contacts: list[SupplierContact] = []
    seen: set[str] = set()

    def push(code: str) -> None:
        if code in seen:
            return
        found = get_supplier_contact(code, scrape_missing=False)
        if found:
            seen.add(code)
            contacts.append(found)

    # 1) Fonte exacta do preço
    if isinstance(price_source, str) and price_source not in (
        "referencia_sectorial",
        "manual",
        "excel",
        "não_encontrado",
    ):
        push(price_source)

    # 2) Fontes consultadas no scrape (mesmo que a mediana tenha vindo de outra)
    for cand in meta.get("candidates") or []:
        if isinstance(cand, dict) and cand.get("source"):
            push(str(cand["source"]))

    # 3) Códigos gravados na ingestão automática
    for code in meta.get("contact_source_codes") or []:
        if isinstance(code, str):
            push(code)

    # 4) Referência setorial → instituições / portais da nota de referência
    if not contacts or price_source == "referencia_sectorial":
        for code in codes_from_reference_context(
            reference_note=str(meta.get("reference_note") or "") or None,
            category=item.category,
            catalog_key=str(meta.get("catalog_key") or "") or None,
            description=item.description,
        ):
            push(code)

    # 5) Portal directo do item
    if not contacts and item.supplier_url:
        contacts.append(
            SupplierContact(
                code="item",
                name=item.supplier_name or "Fornecedor",
                email=None,
                phone=None,
                portal_url=item.supplier_url,
                contact_page=item.supplier_url,
            )
        )

    return [
        {
            "code": c.code,
            "name": c.name,
            "email": c.email,
            "phone": c.phone,
            "portal_url": c.portal_url,
            "contact_page": c.contact_page,
        }
        for c in contacts[:3]
    ]
