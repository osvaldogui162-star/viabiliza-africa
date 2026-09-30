from enum import Enum


class ReportType(str, Enum):
    INTERNATIONAL = "international"
    BFA = "bfa"
    BDA = "bda"

    @classmethod
    def values(cls) -> list[str]:
        return [t.value for t in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.values()

    def label(self) -> str:
        return {
            ReportType.INTERNATIONAL: "Relatório Geral (Modelo Completo)",
            ReportType.BFA: "Relatório BFA (Aviso BNA 10/2020)",
            ReportType.BDA: "Formulário BDA",
        }[self]
