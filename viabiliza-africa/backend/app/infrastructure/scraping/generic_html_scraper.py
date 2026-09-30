"""Scraper genérico HTML com extracção de preço/nome/URL."""

from __future__ import annotations

import re
from decimal import Decimal
from urllib.parse import quote_plus

from app.application.interfaces.market_scraper import IMarketScraper, ScrapedProduct
from app.infrastructure.scraping.http_utils import (
    absolute_url,
    fetch_html_first,
    parse_price,
    strip_tags,
)


class GenericHtmlMarketplaceScraper(IMarketScraper):
    """Base para marketplaces com listagens HTML."""

    def __init__(
        self,
        *,
        code: str,
        name: str,
        base_url: str,
        search_urls: list[str],
        max_results: int = 10,
    ) -> None:
        self._code = code
        self._name = name
        self._base = base_url.rstrip("/")
        self._search_urls = search_urls
        self._max = max_results

    @property
    def source_code(self) -> str:
        return self._code

    def search(self, query: str, *, currency: str = "AOA") -> list[ScrapedProduct]:
        urls = [tpl.format(q=quote_plus(query)) for tpl in self._search_urls]
        try:
            html, used = fetch_html_first(urls, timeout=15)
        except Exception:
            return []
        products = self._extract(html, query, currency, used)
        return products[: self._max]

    def _extract(
        self, html: str, query: str, currency: str, page_url: str
    ) -> list[ScrapedProduct]:
        products: list[ScrapedProduct] = []
        seen: set[str] = set()

        # JSON-LD Product
        for match in re.finditer(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html,
            flags=re.I | re.DOTALL,
        ):
            try:
                import json

                data = json.loads(match.group(1).strip())
            except Exception:
                continue
            items = data if isinstance(data, list) else [data]
            for item in items:
                if not isinstance(item, dict):
                    continue
                types = item.get("@type")
                type_ok = types in ("Product", "ProductGroup") or (
                    isinstance(types, list) and "Product" in types
                )
                if not type_ok:
                    continue
                name = str(item.get("name") or "").strip()
                offers = item.get("offers") or {}
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                price_raw = offers.get("price") if isinstance(offers, dict) else None
                price = parse_price(str(price_raw)) if price_raw is not None else None
                if name and price and price >= Decimal("50"):
                    key = name.lower()[:80]
                    if key not in seen:
                        seen.add(key)
                        href = None
                        if isinstance(offers, dict):
                            href = offers.get("url")
                        products.append(
                            ScrapedProduct(
                                source=self._code,
                                supplier_name=self._name,
                                product_name=name[:200],
                                price=price,
                                currency=currency,
                                product_url=absolute_url(self._base, href) or page_url,
                            )
                        )

        if len(products) >= self._max:
            return products[: self._max]

        # data-price / content price attrs
        for m in re.finditer(
            r'data-price=["\']([\d.,]+)["\'][^>]{0,200}?(?:aria-label|title|alt)=["\']([^"\']{5,120})["\']',
            html,
            flags=re.I,
        ):
            price = parse_price(m.group(1))
            name = m.group(2).strip()
            if price and price >= Decimal("50") and name.lower() not in seen:
                seen.add(name.lower())
                products.append(
                    ScrapedProduct(
                        source=self._code,
                        supplier_name=self._name,
                        product_name=name[:200],
                        price=price,
                        currency=currency,
                        product_url=page_url,
                    )
                )

        # Padrão 1: cartões com preço em Kz/AOA perto de um link
        card_re = re.compile(
            r'<a[^>]+href="([^"]+)"[^>]*>([\s\S]{20,1200}?)</a>',
            flags=re.IGNORECASE,
        )
        price_re = re.compile(
            r"(?:AOA|Kz|KZ|Kwanzas?)\s*([\d.,]+)|([\d.,]+)\s*(?:AOA|Kz|KZ)",
            flags=re.IGNORECASE,
        )

        for href, block in card_re.findall(html):
            if href.startswith("#") or "javascript:" in href.lower():
                continue
            text = strip_tags(block)
            if len(text) < 8:
                continue
            pm = price_re.search(block) or price_re.search(text)
            if not pm:
                continue
            raw_price = pm.group(1) or pm.group(2)
            price = parse_price(raw_price)
            if price is None or price < Decimal("50"):
                continue
            name = text[:180].strip()
            name = re.sub(r"[\d.,]+\s*(?:AOA|Kz|KZ)", "", name, flags=re.I).strip(" -|·•")
            if len(name) < 5:
                continue
            key = name.lower()[:80]
            if key in seen:
                continue
            seen.add(key)
            url = absolute_url(self._base, href) or page_url
            products.append(
                ScrapedProduct(
                    source=self._code,
                    supplier_name=self._name,
                    product_name=name[:200],
                    price=price,
                    currency=currency,
                    product_url=url,
                )
            )
            if len(products) >= self._max:
                break

        if products:
            return products[: self._max]

        # Padrão 2: pares genéricos título + preço no texto limpo
        plain = strip_tags(html)
        for m in re.finditer(
            r"([A-Za-zÀ-ú0-9][^.]{8,80})\s+(?:AOA|Kz|KZ)\s*([\d.,]+)",
            plain,
            flags=re.IGNORECASE,
        ):
            name = m.group(1).strip()
            price = parse_price(m.group(2))
            if price is None or price < Decimal("50"):
                continue
            key = name.lower()
            if key in seen:
                continue
            seen.add(key)
            products.append(
                ScrapedProduct(
                    source=self._code,
                    supplier_name=self._name,
                    product_name=name[:200],
                    price=price,
                    currency=currency,
                    product_url=f"{self._base}/?s={quote_plus(query)}",
                )
            )
            if len(products) >= self._max:
                break
        return products
