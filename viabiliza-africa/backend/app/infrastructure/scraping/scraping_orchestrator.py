from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.application.interfaces.market_scraper import IMarketScraper, ScrapedProduct

logger = logging.getLogger(__name__)

# Marketplaces remotos frequentemente inacessíveis (DNS/timeout) nesta rede
SLOW_REMOTE_SOURCES = frozenset({"jumia", "jiji", "facebook_marketplace"})

# Fontes rápidas locais / regionais
FAST_SOURCES = (
    "kikolo",
    "socia",
    "ovarmat",
    "bricomat",
    "siluz",
    "maxi",
    "moviflor",
    "ncr",
    "sistec",
    "casa_pcs",
    "megatech",
    "gudesom",
)


class ScrapingOrchestrator:
    """Orquestra múltiplos scrapers em paralelo (ondas: lojas locais → remotas)."""

    def __init__(self, scrapers: list[IMarketScraper] | None = None) -> None:
        if scrapers is None:
            from app.infrastructure.scraping.angolan_market_scrapers import (
                build_default_market_scrapers,
            )

            scrapers = build_default_market_scrapers()
        self._scrapers = {s.source_code: s for s in scrapers}

    def available_sources(self) -> list[str]:
        return list(self._scrapers.keys())

    def search(
        self,
        query: str,
        sources: list[str],
        *,
        currency: str = "AOA",
        max_workers: int = 8,
        stop_after: int = 8,
        include_slow_remote: bool = True,
        use_market_board: bool = True,
    ) -> list[ScrapedProduct]:
        """
        Pesquisa em ondas:
        1) Lojas / marketplaces locais
        2) Jumia/Jiji (opcional, lentos)
        3) Tabela de mercado AO (fallback com lojas reais) se ainda vazio
        """
        active = [s for s in sources if s in self._scrapers]
        if not active and not use_market_board:
            return []

        local = [s for s in active if s not in SLOW_REMOTE_SOURCES]
        remote = [s for s in active if s in SLOW_REMOTE_SOURCES] if include_slow_remote else []

        results = self._run_wave(query, local, currency=currency, max_workers=max_workers)
        if len(results) < max(2, stop_after // 2) and remote:
            results.extend(
                self._run_wave(
                    query,
                    remote,
                    currency=currency,
                    max_workers=min(3, max_workers),
                )
            )

        if use_market_board and len(results) < 2:
            from app.domain.catalog.angolan_market_price_board import lookup_market_board

            board = lookup_market_board(query, currency=currency)
            if board:
                logger.info(
                    "Fallback tabela mercado AO '%s': %s oferta(s)", query, len(board)
                )
                results.extend(board)

        return results[: max(stop_after * 2, 12)]

    def _run_wave(
        self,
        query: str,
        sources: list[str],
        *,
        currency: str,
        max_workers: int,
    ) -> list[ScrapedProduct]:
        if not sources:
            return []

        results: list[ScrapedProduct] = []

        def _run(code: str) -> list[ScrapedProduct]:
            try:
                found = self._scrapers[code].search(query, currency=currency)
                if found:
                    logger.info("Scraping %s '%s': %s resultado(s)", code, query, len(found))
                return found
            except Exception as exc:
                logger.info("Scraper %s sem resultados (%s)", code, type(exc).__name__)
                return []

        with ThreadPoolExecutor(max_workers=min(max_workers, len(sources))) as pool:
            futures = {pool.submit(_run, code): code for code in sources}
            for fut in as_completed(futures):
                results.extend(fut.result())

        return results

