"""Scrapers de marketplaces angolanos / regionais."""

from __future__ import annotations

import json
import logging
import re
from decimal import Decimal
from urllib.parse import quote_plus

from app.application.interfaces.market_scraper import IMarketScraper, ScrapedProduct
from app.infrastructure.scraping.generic_html_scraper import GenericHtmlMarketplaceScraper
from app.infrastructure.scraping.http_utils import (
    absolute_url,
    fetch_html,
    fetch_html_first,
    parse_price,
    strip_tags,
)

logger = logging.getLogger(__name__)


class KikoloScraper(GenericHtmlMarketplaceScraper):
    """Kikolo Online — kikoloonline.com."""

    def __init__(self) -> None:
        super().__init__(
            code="kikolo",
            name="Kikolo Online",
            base_url="https://kikoloonline.com",
            search_urls=[
                "https://kikoloonline.com/?s={q}",
                "https://www.kikoloonline.com/?s={q}",
            ],
        )

    def search(self, query: str, *, currency: str = "AOA") -> list[ScrapedProduct]:
        urls = [tpl.format(q=quote_plus(query)) for tpl in self._search_urls]
        try:
            html, used = fetch_html_first(urls, timeout=18)
        except Exception as exc:
            logger.warning("Kikolo scrape failed: %s", exc)
            return []

        products = self._parse_kikolo(html, query, currency, used)
        if not products:
            products = self._extract(html, query, currency, used)
        return products[: self._max]

    def _parse_kikolo(
        self, html: str, query: str, currency: str, page_url: str
    ) -> list[ScrapedProduct]:
        products: list[ScrapedProduct] = []
        # Links /product/<id>
        for href, chunk in re.findall(
            r'href="((?:https?://[^"]+)?/product/[^"]+)"[^>]*>([\s\S]{10,1500}?)</a>',
            html,
            flags=re.I,
        ):
            text = strip_tags(chunk)
            prices = re.findall(r"([\d.,]+)\s*KZ", chunk + " " + text, flags=re.I)
            if not prices:
                continue
            price = parse_price(prices[0])
            if price is None:
                continue
            name = re.sub(r"[\d.,]+\s*KZ", "", text, flags=re.I).strip(" -|")[:200]
            if len(name) < 4:
                continue
            products.append(
                ScrapedProduct(
                    source=self.source_code,
                    supplier_name="Kikolo Online",
                    product_name=name,
                    price=price,
                    currency=currency,
                    product_url=absolute_url(self._base, href) or page_url,
                )
            )
        # JSON embutido
        for m in re.finditer(r'"name"\s*:\s*"([^"]{4,120})"[^}]{0,200}?"(?:price|amount)"\s*:\s*(\d+)', html):
            price = parse_price(m.group(2))
            if price is None:
                continue
            products.append(
                ScrapedProduct(
                    source=self.source_code,
                    supplier_name="Kikolo Online",
                    product_name=m.group(1)[:200],
                    price=price,
                    currency=currency,
                    product_url=f"{self._base}/?s={quote_plus(query)}",
                )
            )
        # dedupe
        seen: set[str] = set()
        unique: list[ScrapedProduct] = []
        for p in products:
            k = p.product_name.lower()
            if k in seen:
                continue
            seen.add(k)
            unique.append(p)
        return unique


class SociaScraper(IMarketScraper):
    """Socia.ao — classificados / marketplace angolano."""

    @property
    def source_code(self) -> str:
        return "socia"

    def search(self, query: str, *, currency: str = "AOA") -> list[ScrapedProduct]:
        urls = [
            f"https://socia.ao/busca?q={quote_plus(query)}",
            f"https://www.socia.ao/search?q={quote_plus(query)}",
            f"https://socia.ao/?s={quote_plus(query)}",
        ]
        # SPA: tentar endpoints JSON comuns
        api_urls = [
            f"https://socia.ao/api/ads?search={quote_plus(query)}",
            f"https://socia.ao/api/listings?q={quote_plus(query)}",
            f"https://api.socia.ao/ads?q={quote_plus(query)}",
        ]
        products: list[ScrapedProduct] = []
        for api in api_urls:
            try:
                raw = fetch_html(api, timeout=10)
                products = self._parse_json(raw, currency)
                if products:
                    return products[:10]
            except Exception:
                continue

        try:
            html, used = fetch_html_first(urls, timeout=15)
        except Exception as exc:
            logger.warning("Socia scrape failed: %s", exc)
            return []
        return GenericHtmlMarketplaceScraper(
            code="socia",
            name="Socia.ao",
            base_url="https://socia.ao",
            search_urls=urls,
        )._extract(html, query, currency, used)[:10]

    def _parse_json(self, raw: str, currency: str) -> list[ScrapedProduct]:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return []
        items = data if isinstance(data, list) else data.get("data") or data.get("results") or data.get("ads") or []
        if not isinstance(items, list):
            return []
        out: list[ScrapedProduct] = []
        for item in items:
            if not isinstance(item, dict):
                continue
            name = str(item.get("title") or item.get("name") or "").strip()
            price_raw = item.get("price") or item.get("amount")
            price = parse_price(str(price_raw)) if price_raw is not None else None
            url = item.get("url") or item.get("link") or item.get("permalink")
            if name and price:
                out.append(
                    ScrapedProduct(
                        source=self.source_code,
                        supplier_name="Socia.ao",
                        product_name=name[:200],
                        price=price,
                        currency=currency,
                        product_url=absolute_url("https://socia.ao", url),
                    )
                )
        return out


class FacebookMarketplaceScraper(IMarketScraper):
    """
    Facebook Marketplace (Angola) — best-effort.
    O Facebook bloqueia frequentemente scrapers anónimos; quando falha, devolve [].
    """

    @property
    def source_code(self) -> str:
        return "facebook_marketplace"

    def search(self, query: str, *, currency: str = "AOA") -> list[ScrapedProduct]:
        # Localização aproximada Luanda
        urls = [
            f"https://www.facebook.com/marketplace/luanda/search/?query={quote_plus(query)}",
            f"https://www.facebook.com/marketplace/angola/search/?query={quote_plus(query)}",
            f"https://m.facebook.com/marketplace/search/?query={quote_plus(query)}&vertical=C2C&location_uid=108394705855671",
        ]
        try:
            html, used = fetch_html_first(urls, timeout=12)
        except Exception as exc:
            logger.info("Facebook Marketplace indisponível para scrape: %s", exc)
            return []

        if "login" in html.lower()[:2000] and "marketplace" not in html.lower():
            logger.info("Facebook Marketplace exige login — sem resultados públicos")
            return []

        products: list[ScrapedProduct] = []
        # JSON embutido marketplace
        for m in re.finditer(
            r'"marketplace_listing_title"\s*:\s*"([^"]+)"[^}]{0,400}?"amount"\s*:\s*"?([\d.]+)"?',
            html,
        ):
            price = parse_price(m.group(2))
            if not price:
                continue
            products.append(
                ScrapedProduct(
                    source=self.source_code,
                    supplier_name="Facebook Marketplace",
                    product_name=m.group(1)[:200],
                    price=price,
                    currency=currency,
                    product_url=used,
                )
            )
        if not products:
            # fallback genérico
            products = GenericHtmlMarketplaceScraper(
                code=self.source_code,
                name="Facebook Marketplace",
                base_url="https://www.facebook.com",
                search_urls=urls,
            )._extract(html, query, currency, used)
        return products[:8]


class PracaDigitalScraper(GenericHtmlMarketplaceScraper):
    """Praça Digital — classificados AO (quando disponível)."""

    def __init__(self) -> None:
        super().__init__(
            code="praca_digital",
            name="Praça Digital",
            base_url="https://pracadigital.ao",
            search_urls=[
                "https://pracadigital.ao/?s={q}",
                "https://www.pracadigital.ao/search?q={q}",
            ],
        )


def build_default_market_scrapers() -> list[IMarketScraper]:
    from app.infrastructure.scraping.angolan_retail_scrapers import (
        build_angolan_retail_scrapers,
    )
    from app.infrastructure.scraping.jumia_scraper import JumiaScraper
    from app.infrastructure.scraping.jiji_scraper import JijiScraper

    return [
        JumiaScraper(),
        JijiScraper(),
        KikoloScraper(),
        SociaScraper(),
        FacebookMarketplaceScraper(),
        PracaDigitalScraper(),
        *build_angolan_retail_scrapers(),
    ]
