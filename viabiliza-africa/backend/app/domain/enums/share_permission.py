from enum import Enum


class SharePermission(str, Enum):
    """Nível de acesso de um utilizador partilhado."""

    VIEW = "view"
    COLLABORATE = "collaborate"

    @classmethod
    def values(cls) -> list[str]:
        return [p.value for p in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.values()
