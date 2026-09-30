from uuid import UUID

from app.application.services.collaboration_access_policy import CollaborationAccessPolicy
from app.application.services.kanban_board_service import KanbanBoardService
from app.application.services.kanban_task_service import KanbanTaskService
from app.application.services.project_context_resolver import ProjectContextResolver
from app.domain.enums.kanban_provider import KanbanProvider
from app.domain.exceptions.domain_exceptions import AuthorizationError


class GetKanbanIntegrationUseCase:
    """Metadados do board Kanban (Trello) para embed no frontend."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        collaboration_policy: CollaborationAccessPolicy,
        board_service: KanbanBoardService,
    ) -> None:
        self._ctx = context_resolver
        self._policy = collaboration_policy
        self._boards = board_service

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_collaborate(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para aceder ao Kanban")

        integration = self._boards.ensure_board(ctx.project)
        provider = self._boards.active_provider.value
        external = self._boards.is_external_enabled()

        payload = {
            "provider": provider,
            "external_enabled": external,
            "board_url": None,
            "external_board_id": None,
            "embed_url": None,
        }

        if integration and integration.external_board_id:
            payload.update(
                {
                    "board_url": integration.board_url,
                    "external_board_id": integration.external_board_id,
                    "embed_url": (
                        f"{integration.board_url}"
                        if integration.board_url
                        else None
                    ),
                    "list_map": integration.list_map,
                }
            )

        return payload


class SyncKanbanBoardUseCase:
    """Sincroniza cartões do Trello para a API local."""

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        collaboration_policy: CollaborationAccessPolicy,
        board_service: KanbanBoardService,
        kanban_task_service: KanbanTaskService,
    ) -> None:
        self._ctx = context_resolver
        self._policy = collaboration_policy
        self._boards = board_service
        self._tasks = kanban_task_service

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_collaborate(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para sincronizar o Kanban")

        if not self._boards.is_external_enabled():
            return {
                "provider": KanbanProvider.LOCAL.value,
                "synced": 0,
                "message": "Integração externa desactivada (KANBAN_PROVIDER=local)",
            }

        synced = self._tasks.sync_from_external(ctx.project, owner_id=ctx.project.owner_id)
        integration = self._boards.get_integration(project_id)
        return {
            "provider": KanbanProvider.TRELLO.value,
            "synced": synced,
            "board_url": integration.board_url if integration else None,
            "message": f"{synced} cartão(ões) sincronizado(s) do Trello",
        }
