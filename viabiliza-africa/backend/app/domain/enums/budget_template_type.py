from enum import Enum


class BudgetTemplateType(str, Enum):
    BUDGET = "budget"
    PROFORMA = "proforma"
    BOTH = "both"

    @classmethod
    def values(cls) -> list[str]:
        return [t.value for t in cls]
