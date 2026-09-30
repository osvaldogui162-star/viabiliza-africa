from uuid import UUID

from app.application.services.collaboration_access_policy import CollaborationAccessPolicy
from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.use_cases.collaboration.mappers import to_chat_message_output
from app.domain.exceptions.domain_exceptions import AuthorizationError
from app.domain.repositories.collaboration_repository import (
    IChatMessageRepository,
    IChatReadStateRepository,
    IProjectPresenceRepository,
)
from app.domain.repositories.user_repository import IUserRepository


class PollChatUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        collaboration_policy: CollaborationAccessPolicy,
        chat_repository: IChatMessageRepository,
        read_state_repository: IChatReadStateRepository,
        presence_repository: IProjectPresenceRepository,
        user_repository: IUserRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = collaboration_policy
        self._chat = chat_repository
        self._read = read_state_repository
        self._presence = presence_repository
        self._users = user_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        after_id: UUID | None = None,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_collaborate(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para visualizar o chat")

        self._presence.heartbeat(user_id=actor_id, project_id=project_id)
        messages = self._chat.find_after(project_id, after_id, limit=50)
        sender_ids = list({m.sender_id for m in messages})
        users = self._users.find_by_ids(sender_ids)

        online_ids = self._presence.list_online(project_id)
        online_users = self._users.find_by_ids(online_ids)

        return {
            "messages": [
                to_chat_message_output(
                    m,
                    user_name=users.get(m.sender_id).full_name if users.get(m.sender_id) else None,
                )
                for m in messages
            ],
            "online": [
                {"user_id": str(uid), "name": online_users[uid].full_name}
                for uid in online_ids
                if uid in online_users
            ],
        }


class MarkChatReadUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        collaboration_policy: CollaborationAccessPolicy,
        read_state_repository: IChatReadStateRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = collaboration_policy
        self._read = read_state_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        message_id: UUID | None = None,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_collaborate(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão")

        self._read.upsert_read(user_id=actor_id, project_id=project_id, message_id=message_id)
        return {"message": "ok"}


class ChatPresenceUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        collaboration_policy: CollaborationAccessPolicy,
        presence_repository: IProjectPresenceRepository,
        user_repository: IUserRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = collaboration_policy
        self._presence = presence_repository
        self._users = user_repository

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_collaborate(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão")

        self._presence.heartbeat(user_id=actor_id, project_id=project_id)
        online_ids = self._presence.list_online(project_id)
        users = self._users.find_by_ids(online_ids)
        return {
            "online": [
                {"user_id": str(uid), "name": users[uid].full_name}
                for uid in online_ids
                if uid in users
            ],
        }
