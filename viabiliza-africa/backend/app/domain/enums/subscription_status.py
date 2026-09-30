from enum import Enum


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"

    @classmethod
    def values(cls) -> list[str]:
        return [s.value for s in cls]
