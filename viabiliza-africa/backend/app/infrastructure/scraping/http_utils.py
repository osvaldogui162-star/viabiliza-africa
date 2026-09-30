from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from urllib.parse import quote_plus, urljoin

import requests

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
}


def fetch_html(url: str, *, timeout: int = 6) -> str:
    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or "utf-8"
    return response.text


def fetch_html_first(urls: list[str], *, timeout: int = 6) -> tuple[str, str]:
    """Tenta várias URLs; devolve (html, url_usada)."""
    last_error: Exception | None = None
    for url in urls:
        try:
            return fetch_html(url, timeout=timeout), url
        except Exception as exc:
            last_error = exc
    raise last_error or RuntimeError("Nenhuma URL disponível")


def parse_price(raw: str) -> Decimal | None:
    if not raw:
        return None
    cleaned = re.sub(r"[^\d,.\-]", "", raw.strip())
    if not cleaned:
        return None
    # Formatos AO: 12.500,00 ou 12500,00 ou 12,500.00
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        parts = cleaned.split(",")
        cleaned = cleaned.replace(",", ".") if len(parts[-1]) <= 2 else cleaned.replace(",", "")
    try:
        value = Decimal(cleaned)
        return value if value > 0 else None
    except InvalidOperation:
        return None


def absolute_url(base: str, href: str | None) -> str | None:
    if not href:
        return None
    return urljoin(base, href)


def search_url(base: str, path: str, query: str) -> str:
    return f"{base.rstrip('/')}{path}{quote_plus(query)}"


def strip_tags(html: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.IGNORECASE)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()
