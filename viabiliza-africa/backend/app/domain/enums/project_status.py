from enum import Enum


class ProjectStatus(str, Enum):
    """Estados do ciclo de vida de um projeto de viabilidade."""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    ARCHIVED = "archived"

    @classmethod
    def values(cls) -> list[str]:
        return [s.value for s in cls]

    @classmethod
    def is_valid(cls, value: str) -> bool:
        return value in cls.values()

    def is_editable(self) -> bool:
        return self == ProjectStatus.DRAFT

    @property
    def label_pt(self) -> str:
        labels = {
            ProjectStatus.DRAFT: "Rascunho",
            ProjectStatus.IN_PROGRESS: "Em Andamento",
            ProjectStatus.UNDER_REVIEW: "Em Revisão",
            ProjectStatus.APPROVED: "Aprovado",
            ProjectStatus.ARCHIVED: "Arquivado",
        }
        return labels[self]
