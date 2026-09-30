from enum import Enum


class Currency(str, Enum):
    """Moedas suportadas para estudos de viabilidade."""

    USD = "USD"
    EUR = "EUR"
    AOA = "AOA"
    ZAR = "ZAR"
    NGN = "NGN"
    KES = "KES"
    GHS = "GHS"
    MZN = "MZN"
    TZS = "TZS"
    XOF = "XOF"
    XAF = "XAF"

    @classmethod
    def values(cls) -> list[str]:
        return [c.value for c in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value.upper() in cls.values()
