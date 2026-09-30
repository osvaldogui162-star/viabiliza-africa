"""Tipos de financiamento bancário para projectos."""

from enum import Enum


class FinancingType(str, Enum):
    INVESTMENT_CREDIT = "investment_credit"
    CREDIT_LINE = "credit_line"
    LEASING = "leasing"
    MIXED = "mixed"
    GRANT = "grant"

    @classmethod
    def values(cls) -> list[str]:
        return [m.value for m in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.values()

    @property
    def label_pt(self) -> str:
        return _LABELS.get(self, self.value)


_LABELS = {
    FinancingType.INVESTMENT_CREDIT: "Crédito de investimento",
    FinancingType.CREDIT_LINE: "Linha de crédito",
    FinancingType.LEASING: "Leasing financeiro",
    FinancingType.MIXED: "Misto (capital + dívida)",
    FinancingType.GRANT: "Subsídio / grant",
}
