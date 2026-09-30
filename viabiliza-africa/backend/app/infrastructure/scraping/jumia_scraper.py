from __future__ import annotations

import json
import logging
import re
from decimal import Decimal
from urllib.parse import quote_plus

from app.application.interfaces.market_scraper import IMarketScraper, ScrapedProduct
from app.infrastructure.scraping.http_utils import (
    absolute_url,
    fetch_html_first,
    parse_price,
)

logger = logging.getLogger(__name__)

JUMIA_BASE = "https://www.jumia.ao"


class JumiaScraper(IMarketScraper):
    """Scraper Jumia Angola — pesquisa real em jumia.ao."""

    @property
    def source_code(self) -> str:
        return "jumia"

    def search(self, query: str, *, currency: str = "AOA") -> list[ScrapedProduct]:
        urls = [
            f"{JUMIA_BASE}/catalog/?q={quote_plus(query)}",
            f"https://jumia.ao/catalog/?q={quote_plus(query)}",
        ]
        try:
            html, _ = fetch_html_first(urls, timeout=4)
        except Exception as exc:
            # DNS/timeout são esperados em redes sem acesso a jumia.ao
            logger.info("Jumia indisponível para %r: %s", query, exc)
            return []

        products = self._parse_json_ld(html, currency) or self._parse_catalog_cards(
            html, query, currency
        )
        return products[:12]

    def _parse_json_ld(self, html: str, currency: str) -> list[ScrapedProduct]:
        products: list[ScrapedProduct] = []
        for match in re.finditer(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            html,
            flags=re.IGNORECASE | re.DOTALL,
        ):
            raw = match.group(1).strip()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            items = data if isinstance(data, list) else [data]
            for item in items:
                products.extend(self._from_ld_item(item, currency))
        return products

    def _from_ld_item(self, item: dict, currency: str) -> list[ScrapedProduct]:
        if not isinstance(item, dict):
            return []
        results: list[ScrapedProduct] = []
        item_type = item.get("@type")
        if item_type == "ItemList":
            for element in item.get("itemListElement", []):
                entity = element.get("item", element) if isinstance(element, dict) else None
                if isinstance(entity, dict):
                    results.extend(self._from_ld_item(entity, currency))
            return results
        if item_type not in ("Product", "ProductGroup"):
            return []

        name = (item.get("name") or "").strip()
        offers = item.get("offers") or {}
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        price_raw = offers.get("price") if isinstance(offers, dict) else None
        price = parse_price(str(price_raw)) if price_raw is not None else None
        offer_currency = (
            offers.get("priceCurrency", currency) if isinstance(offers, dict) else currency
        )
        url = item.get("url") or (offers.get("url") if isinstance(offers, dict) else None)
        if name and price is not None:
            results.append(
                ScrapedProduct(
                    source=self.source_code,
                    supplier_name="Jumia Angola",
                    product_name=name[:200],
                    price=price,
                    currency=str(offer_currency or currency),
                    product_url=absolute_url(JUMIA_BASE, url),
                )
            )
        return results

    def _parse_catalog_cards(
        self, html: str, query: str, currency: str
    ) -> list[ScrapedProduct]:
        products: list[ScrapedProduct] = []
        # Cartões de produto Jumia: article.prd
        cards = re.findall(
            r'<article[^>]*class="[^"]*prd[^"]*"[^>]*>(.*?)</article>',
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )
        for card in cards:
            name_match = re.search(
                r'class="name"[^>]*>(.*?)</',
                card,
                flags=re.IGNORECASE | re.DOTALL,
            )
            price_match = re.search(
                r'class="prc"[^>]*>(.*?)</',
                card,
                flags=re.IGNORECASE | re.DOTALL,
            )
            href_match = re.search(
                r'href="([^"]+)"',
                card,
                flags=re.IGNORECASE,
            )
            if not name_match or not price_match:
                continue
            name = re.sub(r"<[^>]+>", "", name_match.group(1)).strip()
            price = parse_price(re.sub(r"<[^>]+>", "", price_match.group(1)))
            if not name or price is None:
                continue
            products.append(
                ScrapedProduct(
                    source=self.source_code,
                    supplier_name="Jumia Angola",
                    product_name=name[:200],
                    price=price,
                    currency=currency,
                    product_url=absolute_url(
                        JUMIA_BASE, href_match.group(1) if href_match else None
                    )
                    or f"{JUMIA_BASE}/catalog/?q={quote_plus(query)}",
                )
            )
        return products
