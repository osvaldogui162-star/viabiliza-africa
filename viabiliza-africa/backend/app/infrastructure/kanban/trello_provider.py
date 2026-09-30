from datetime import date, datetime

from app.application.interfaces.kanban_provider import (
    ExternalKanbanBoard,
    ExternalKanbanCard,
    IKanbanProvider,
)
from app.domain.enums.task_status import TaskStatus
from app.infrastructure.kanban.trello_client import TrelloClient

# Mapeamento colunas ViabilizA+ ↔ listas Trello
LIST_LABELS = {
    TaskStatus.TODO: "A Fazer",
    TaskStatus.IN_PROGRESS: "Em Andamento",
    TaskStatus.DONE: "Concluído",
}


class TrelloKanbanProvider(IKanbanProvider):
    """Integração com Trello — Kanban real via API."""

    def __init__(self, client: TrelloClient) -> None:
        self._client = client

    def create_board(self, name: str) -> ExternalKanbanBoard:
        board = self._client.post(
            "/boards",
            name=name[:163],
            defaultLists="false",
            prefs_permissionLevel="private",
        )
        board_id = board["id"]
        list_map: dict[str, str] = {}
        for status in (TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.DONE):
            lst = self._client.post(
                "/lists",
                name=LIST_LABELS[status],
                idBoard=board_id,
            )
            list_map[status.value] = lst["id"]

        short_url = board.get("shortUrl") or f"https://trello.com/b/{board.get('shortLink', board_id)}"
        return ExternalKanbanBoard(
            external_board_id=board_id,
            board_url=short_url,
            list_map=list_map,
            metadata={"short_link": board.get("shortLink")},
        )

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
        list_id = board.list_map[status.value]
        params: dict = {
            "name": title[:163],
            "idList": list_id,
            "pos": position + 1,
        }
        if description:
            params["desc"] = description[:16384]
        if due_date:
            params["due"] = datetime.combine(due_date, datetime.min.time()).isoformat() + "Z"

        card = self._client.post("/cards", **params)
        return self._map_card(card, board)

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
        params: dict = {}
        if title is not None:
            params["name"] = title[:163]
        if description is not None:
            params["desc"] = description[:16384] if description else ""
        if due_date is not ...:
            params["due"] = (
                datetime.combine(due_date, datetime.min.time()).isoformat() + "Z"
                if due_date
                else "null"
            )
        if status is not None:
            params["idList"] = board.list_map[status.value]
        if position is not None:
            params["pos"] = position + 1

        card = self._client.put(f"/cards/{external_id}", **params)
        return self._map_card(card, board)

    def delete_card(self, external_id: str) -> None:
        self._client.delete(f"/cards/{external_id}")

    def list_cards(self, board: ExternalKanbanBoard) -> list[ExternalKanbanCard]:
        cards = self._client.get(f"/boards/{board.external_board_id}/cards")
        return [self._map_card(card, board) for card in cards]

    def _map_card(self, card: dict, board: ExternalKanbanBoard) -> ExternalKanbanCard:
        list_id = card["idList"]
        status_value = None
        for st, lid in board.list_map.items():
            if lid == list_id:
                status_value = st
                break
        status = TaskStatus(status_value) if status_value else TaskStatus.TODO

        due = None
        if card.get("due"):
            due = datetime.fromisoformat(card["due"].replace("Z", "+00:00")).date()

        return ExternalKanbanCard(
            external_id=card["id"],
            title=card["name"],
            description=card.get("desc") or None,
            status=status,
            position=int(card.get("pos", 0)),
            due_date=due,
            board_id=board.external_board_id,
            list_id=list_id,
        )
