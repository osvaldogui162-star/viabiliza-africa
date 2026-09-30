from __future__ import annotations

import json
import logging
import re
from urllib.parse import quote_plus

from app.application.interfaces.market_scraper import IMarketScraper, ScrapedProduct
from app.infrastructure.scraping.http_utils import (
    absolute_url,
    fetch_html_first,
    parse_price,
)

logger = logging.getLogger(__name__)

JIJI_BASE = "https://jiji.ao"


class JijiScraper(IMarketScraper):
    """Scraper Jiji Angola — pesquisa real em jiji.ao."""

    @property
    def source_code(self) -> str:
        return "jiji"

    def search(self, query: str, *, currency: str = "AOA") -> list[ScrapedProduct]:
        urls = [
            f"{JIJI_BASE}/search?query={quote_plus(query)}",
            f"https://www.jiji.ao/search?query={quote_plus(query)}",
        ]
        try:
            html, _ = fetch_html_first(urls, timeout=4)
        except Exception as exc:
            logger.info("Jiji indisponível para %r: %s", query, exc)
            return []

        products = self._parse_embedded_json(html, currency) or self._parse_listing_cards(
            html, query, currency
        )
        return products[:12]

    def _parse_embedded_json(self, html: str, currency: str) -> list[ScrapedProduct]:
        products: list[ScrapedProduct] = []
        # Jiji frequentemente embute dados em window.__INITIAL_STATE__ ou similar
        for pattern in (
            r"window\.__NUXT__\s*=\s*(\{.*?\});?\s*</script>",
            r'"adverts"\s*:\s*(\[[^\]]{20,}\])',
            r'"items"\s*:\s*(\[[^\]]{20,}\])',
        ):
            match = re.search(pattern, html, flags=re.DOTALL)
            if not match:
                continue
            raw = match.group(1)
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            items = data if isinstance(data, list) else []
            for item in items:
                if not isinstance(item, dict):
                    continue
                name = (
                    item.get("title")
                    or item.get("name")
                    or item.get("advert_title")
                    or ""
                ).strip()
                price_obj = item.get("price_obj")
                price_raw = item.get("price")
                if price_raw is None and isinstance(price_obj, dict):
                    price_raw = price_obj.get("value")
                price = parse_price(str(price_raw)) if price_raw is not None else None
                href = item.get("url") or item.get("absolute_url") or item.get("slug")
                if name and price is not None:
                    products.append(
                        ScrapedProduct(
                            source=self.source_code,
                            supplier_name="Jiji Angola",
                            product_name=name[:200],
                            price=price,
                            currency=currency,
                            product_url=absolute_url(JIJI_BASE, href),
                        )
                    )
            if products:
                break
        return products

    def _parse_listing_cards(
        self, html: str, query: str, currency: str
    ) -> list[ScrapedProduct]:
        products: list[ScrapedProduct] = []
        cards = re.findall(
            r'<div[^>]*class="[^"]*(?:b-list-advert|qa-advert-list-item|advert)[^"]*"[^>]*>'
            r"(.*?)</div>\s*</div>",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )
        if not cards:
            # Fallback: pares título + preço próximos no HTML
            pairs = re.findall(
                r'(?:data-testid="ad-title"|class="[^"]*title[^"]*")[^>]*>(.*?)</[^>]+>'
                r'[\s\S]{0,400}?(?:class="[^"]*price[^"]*"|data-testid="ad-price")[^>]*>'
                r"(.*?)</",
                html,
                flags=re.IGNORECASE,
            )
            for name_html, price_html in pairs:
                name = re.sub(r"<[^>]+>", "", name_html).strip()
                price = parse_price(re.sub(r"<[^>]+>", "", price_html))
                if name and price is not None:
                    products.append(
                        ScrapedProduct(
                            source=self.source_code,
                            supplier_name="Jiji Angola",
                            product_name=name[:200],
                            price=price,
                            currency=currency,
                            product_url=f"{JIJI_BASE}/search?query={quote_plus(query)}",
                        )
                    )
            return products

        for card in cards:
            name_match = re.search(
                r'(?:qa-advert-title|advert-title|b-advert-title)[^>]*>(.*?)</',
                card,
                flags=re.IGNORECASE | re.DOTALL,
            )
            price_match = re.search(
                r'(?:qa-advert-price|advert-price|b-advert-price)[^>]*>(.*?)</',
                card,
                flags=re.IGNORECASE | re.DOTALL,
            )
            href_match = re.search(r'href="([^"]+)"', card, flags=re.IGNORECASE)
            if not name_match or not price_match:
                continue
            name = re.sub(r"<[^>]+>", "", name_match.group(1)).strip()
            price = parse_price(re.sub(r"<[^>]+>", "", price_match.group(1)))
            if not name or price is None:
                continue
            products.append(
                ScrapedProduct(
                    source=self.source_code,
                    supplier_name="Jiji Angola",
                    product_name=name[:200],
                    price=price,
                    currency=currency,
                    product_url=absolute_url(
                        JIJI_BASE, href_match.group(1) if href_match else None
                    )
                    or f"{JIJI_BASE}/search?query={quote_plus(query)}",
                )
            )
        return products
