"""Scrapers genéricos para retalhistas angolanos com loja online."""

from __future__ import annotations

from app.application.interfaces.market_scraper import IMarketScraper
from app.domain.catalog.angolan_retail_suppliers import scrapable_suppliers
from app.infrastructure.scraping.generic_html_scraper import GenericHtmlMarketplaceScraper


def build_angolan_retail_scrapers() -> list[IMarketScraper]:
    """Cria um GenericHtmlMarketplaceScraper por retalhista com search_urls."""
    scrapers: list[IMarketScraper] = []
    for supplier in scrapable_suppliers():
        scrapers.append(
            GenericHtmlMarketplaceScraper(
                code=supplier.code,
                name=supplier.name,
                base_url=supplier.base_url,
                search_urls=list(supplier.search_urls),
                max_results=8,
            )
        )
    return scrapers
