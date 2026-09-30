from enum import Enum


class RegistrationMode(str, Enum):
    OPEN = "open"
    INVITE_ONLY = "invite_only"
    ADMIN_APPROVAL = "admin_approval"

    @classmethod
    def values(cls) -> list[str]:
        return [m.value for m in cls]

    @classmethod
    def parse(cls, value: str | None) -> "RegistrationMode":
        if not value:
            return cls.ADMIN_APPROVAL
        try:
            return cls(value.strip().lower())
        except ValueError:
            return cls.ADMIN_APPROVAL
