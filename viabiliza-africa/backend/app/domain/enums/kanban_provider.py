from enum import Enum


class KanbanProvider(str, Enum):
    LOCAL = "local"
    TRELLO = "trello"

    @classmethod
    def values(cls) -> list[str]:
        return [p.value for p in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.values()
