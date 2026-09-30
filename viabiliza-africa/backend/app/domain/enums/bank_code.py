from enum import Enum


class BankCode(str, Enum):
    BFA = "bfa"
    BDA = "bda"

    @classmethod
    def values(cls) -> list[str]:
        return [b.value for b in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.values()
