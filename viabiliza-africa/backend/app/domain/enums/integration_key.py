from enum import Enum


class IntegrationKey(str, Enum):
    BFA = "bfa"
    BDA = "bda"
    SMTP = "smtp"
    TRELLO = "trello"

    @classmethod
    def values(cls) -> list[str]:
        return [k.value for k in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.values()
