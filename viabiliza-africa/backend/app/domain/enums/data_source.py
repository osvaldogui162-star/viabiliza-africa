from enum import Enum


class DataSource(str, Enum):
    MANUAL = "manual"
    EXCEL = "excel"
    SCRAPING = "scraping"

    @classmethod
    def values(cls) -> list[str]:
        return [s.value for s in cls]
