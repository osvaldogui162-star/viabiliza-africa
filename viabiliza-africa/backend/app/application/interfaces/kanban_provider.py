from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date

from app.domain.enums.task_status import TaskStatus


@dataclass
class ExternalKanbanBoard:
    external_board_id: str
    board_url: str
    list_map: dict[str, str] = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)


@dataclass
class ExternalKanbanCard:
    external_id: str
    title: str
    description: str | None
    status: TaskStatus
    position: int
    due_date: date | None
    board_id: str
    list_id: str


class IKanbanProvider(ABC):
    """Contrato para provedores Kanban externos (Strategy)."""

    @abstractmethod
    def create_board(self, name: str) -> ExternalKanbanBoard:
        ...

    @abstractmethod
    def create_card(
        self,
        board: ExternalKanbanBoard,
        *,
        title: str,
        description: str | None,
        due_date: date | None,
        status: TaskStatus,
        position: int,
    ) -> ExternalKanbanCard:
        ...

    @abstractmethod
    def update_card(
        self,
        board: ExternalKanbanBoard,
        external_id: str,
        *,
        title: str | None = None,
        description: str | None = None,
        due_date: date | None = ...,
        status: TaskStatus | None = None,
        position: int | None = None,
    ) -> ExternalKanbanCard:
        ...

    @abstractmethod
    def delete_card(self, external_id: str) -> None:
        ...

    @abstractmethod
    def list_cards(self, board: ExternalKanbanBoard) -> list[ExternalKanbanCard]:
        ...
