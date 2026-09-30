from uuid import UUID

from app.application.services.collaboration_access_policy import CollaborationAccessPolicy
from app.application.services.notification_service import NotificationService
from app.application.services.project_context_resolver import ProjectContextResolver
from app.application.use_cases.collaboration.mappers import to_chat_message_output
from app.domain.exceptions.domain_exceptions import AuthorizationError, ValidationError
from app.domain.repositories.collaboration_repository import IChatMessageRepository
from app.domain.repositories.project_share_repository import IProjectShareRepository
from app.domain.repositories.user_repository import IUserRepository


class SendChatMessageUseCase:
    """UC27 — Enviar mensagem no chat do projeto."""

    MAX_LENGTH = 5000

    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        collaboration_policy: CollaborationAccessPolicy,
        chat_repository: IChatMessageRepository,
        user_repository: IUserRepository,
        project_share_repository: IProjectShareRepository | None = None,
        notification_service: NotificationService | None = None,
    ) -> None:
        self._ctx = context_resolver
        self._policy = collaboration_policy
        self._chat = chat_repository
        self._users = user_repository
        self._shares = project_share_repository
        self._notifications = notification_service

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        content: str,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_collaborate(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para enviar mensagens neste projeto")

        content = content.strip()
        if not content:
            raise ValidationError("Mensagem não pode estar vazia")
        if len(content) > self.MAX_LENGTH:
            raise ValidationError(f"Mensagem não pode exceder {self.MAX_LENGTH} caracteres")

        message = self._chat.create(
            project_id=project_id,
            sender_id=actor_id,
            content=content,
        )
        sender = self._users.find_by_id(actor_id)
        sender_name = sender.full_name if sender else "Utilizador"

        if self._notifications and self._shares:
            member_ids = [ctx.project.owner_id]
            shares = self._shares.find_by_project(project_id)
            member_ids.extend(s.user_id for s in shares)
            unique_members = list({m for m in member_ids if m})
            project_name = ctx.project.name or "Projecto"
            self._notifications.notify_chat_message(
                project_id=project_id,
                project_name=project_name,
                sender_id=actor_id,
                sender_name=sender_name,
                content=content,
                member_ids=unique_members,
            )
            self._notifications.notify_chat_mentions(
                project_id=project_id,
                sender_id=actor_id,
                sender_name=sender_name,
                content=content,
                member_ids=unique_members,
            )

        return to_chat_message_output(message, user_name=sender_name)


class ListChatMessagesUseCase:
    def __init__(
        self,
        context_resolver: ProjectContextResolver,
        collaboration_policy: CollaborationAccessPolicy,
        chat_repository: IChatMessageRepository,
        user_repository: IUserRepository,
    ) -> None:
        self._ctx = context_resolver
        self._policy = collaboration_policy
        self._chat = chat_repository
        self._users = user_repository

    def execute(
        self,
        *,
        actor_id: UUID,
        project_id: UUID,
        limit: int = 50,
        before_id: UUID | None = None,
    ) -> dict:
        ctx = self._ctx.resolve(actor_id, project_id)
        if not self._policy.can_collaborate(ctx.actor, ctx.project, is_shared=ctx.is_shared):
            raise AuthorizationError("Não tem permissão para visualizar o chat")

        messages = self._chat.find_by_project(
            project_id, limit=min(limit, 100), before_id=before_id
        )
        sender_ids = list({m.sender_id for m in messages})
        users = self._users.find_by_ids(sender_ids)
        return {
            "items": [
                to_chat_message_output(
                    m,
                    user_name=users.get(m.sender_id).full_name if users.get(m.sender_id) else None,
                )
                for m in messages
            ],
            "total": len(messages),
        }
