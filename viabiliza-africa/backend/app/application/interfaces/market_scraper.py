from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ScrapedProduct:
    source: str
    supplier_name: str
    product_name: str
    price: Decimal
    currency: str
    product_url: str | None


class IMarketScraper(ABC):
    """Strategy Pattern — scraper de marketplace africano."""

    @property
    @abstractmethod
    def source_code(self) -> str:
        ...

    @abstractmethod
    def search(self, query: str, *, currency: str = "AOA") -> list[ScrapedProduct]:
        ...
