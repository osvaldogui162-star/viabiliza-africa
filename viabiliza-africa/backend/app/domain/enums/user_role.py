from enum import Enum


class UserRole(str, Enum):
    """Perfis de acesso do sistema (RBAC)."""

    ADMIN = "admin"
    FINANCIAL = "financial"
    USER = "user"
    BANK = "bank"

    @classmethod
    def values(cls) -> list[str]:
        return [role.value for role in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.values()
