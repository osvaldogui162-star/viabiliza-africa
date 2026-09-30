from enum import Enum


class ReportLanguage(str, Enum):
    PT = "pt"
    EN = "en"

    @classmethod
    def values(cls) -> list[str]:
        return [l.value for l in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.values()
