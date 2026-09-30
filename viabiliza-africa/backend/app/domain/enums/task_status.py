from enum import Enum


class TaskStatus(str, Enum):
    """Estados do Kanban — A Fazer → Em Andamento → Revisão → Concluído."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"

    @classmethod
    def values(cls) -> list[str]:
        return [s.value for s in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.values()

    def label(self) -> str:
        return {
            TaskStatus.TODO: "A Fazer",
            TaskStatus.IN_PROGRESS: "Em Andamento",
            TaskStatus.REVIEW: "Em Revisão",
            TaskStatus.DONE: "Concluído",
        }[self]
