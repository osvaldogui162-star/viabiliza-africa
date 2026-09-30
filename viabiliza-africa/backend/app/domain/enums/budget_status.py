from enum import Enum


class BudgetStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    SUPERSEDED = "superseded"

    @classmethod
    def values(cls) -> list[str]:
        return [s.value for s in cls]
