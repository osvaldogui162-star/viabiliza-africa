from enum import Enum


class CostItemType(str, Enum):
    """Tipo de item de custo (CAPEX ou OPEX)."""

    CAPEX = "capex"
    OPEX = "opex"

    @classmethod
    def values(cls) -> list[str]:
        return [t.value for t in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.values()
