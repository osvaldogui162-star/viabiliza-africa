from uuid import UUID

from app.application.dto.project_dto import (
    ProjectShareOutput,
    RemoveProjectShareInput,
    ShareProjectInput,
    ShareProjectResult,
)
from app.application.services.project_access_policy import ProjectAccessPolicy
from app.application.services.registration_policy_service import RegistrationPolicyService
from app.application.services.subscription_service import SubscriptionService
from app.application.services.notification_service import NotificationService
from app.application.use_cases.projects.project_mapper import to_share_output
from app.domain.enums.access_action import AccessAction
from app.domain.enums.share_permission import SharePermission
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.domain_exceptions import (
    AuthorizationError,
    ConflictError,
    EntityNotFoundError,
    ValidationError,
)
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.project_share_repository import IProjectShareRepository
from app.domain.repositories.user_repository import IUserRepository


class ShareProjectUseCase:
    """UC11 — Partilhar projeto com outro utilizador."""

    def __init__(
        self,
        user_repository: IUserRepository,
        project_repository: IProjectRepository,
        project_share_repository: IProjectShareRepository,
        access_log_repository: IAccessLogRepository,
        access_policy: ProjectAccessPolicy,
        registration_policy: RegistrationPolicyService,
        subscription_service: SubscriptionService | None = None,
        notification_service: NotificationService | None = None,
    ) -> None:
        self._users = user_repository
        self._projects = project_repository
        self._shares = project_share_repository
        self._access_logs = access_log_repository
        self._policy = access_policy
        self._registration = registration_policy
        self._subscription = subscription_service
        self._notifications = notification_service

    def execute(self, input_data: ShareProjectInput) -> ShareProjectResult | ProjectShareOutput:
        actor = self._users.find_by_id(input_data.actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(input_data.actor_id))

        project = self._projects.find_by_id(input_data.project_id)
        if project is None:
            raise EntityNotFoundError("Projeto", str(input_data.project_id))

        if not self._policy.can_share(actor, project):
            raise AuthorizationError("Não tem permissão para partilhar este projeto")

        if not SharePermission.is_valid(input_data.permission):
            raise ValidationError(
                f"Permissão inválida. Valores: {', '.join(SharePermission.values())}"
            )

        target_email = input_data.user_email.strip().lower()
        target = self._users.find_by_email(target_email)

        if target is None:
            invite = self._registration.create_project_invite(
                email=target_email,
                invited_by=actor.id,
                project_id=input_data.project_id,
                permission=input_data.permission,
                capabilities=input_data.capabilities,
                office_member_id=input_data.office_member_id,
                job_title=input_data.job_title,
            )
            self._access_logs.create(
                user_id=actor.id,
                action=AccessAction.PROJECT_SHARED,
                ip_address=input_data.ip_address,
                user_agent=input_data.user_agent,
                metadata={
                    "project_id": str(input_data.project_id),
                    "pending_invite_email": target_email,
                    "permission": input_data.permission,
                },
            )
            return ShareProjectResult(
                pending_invite=True,
                invite_email=target_email,
                message=(
                    "Convite enviado. Quando o colaborador criar conta com este email, "
                    "terá acesso automático ao projecto."
                ),
                expires_at=invite.expires_at,
            )

        if not target.is_active:
            raise ValidationError(
                "A conta deste utilizador ainda aguarda aprovação. "
                "Aguarde a activação ou partilhe após aprovação."
            )

        if target.role == UserRole.ADMIN:
            raise ValidationError("Não é possível partilhar projeto com administradores")

        if target.id == project.owner_id:
            raise ValidationError("O proprietário do projeto já tem acesso total")

        existing = self._shares.find_by_project_and_user(input_data.project_id, target.id)
        if existing:
            raise ConflictError("Projeto já partilhado com este utilizador")

        if self._subscription:
            self._subscription.ensure_can_add_collaborator(actor, target.id)

        share = self._shares.create(
            project_id=input_data.project_id,
            user_id=target.id,
            shared_by=actor.id,
            permission=SharePermission(input_data.permission),
        )

        self._access_logs.create(
            user_id=actor.id,
            action=AccessAction.PROJECT_SHARED,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
            metadata={
                "project_id": str(input_data.project_id),
                "shared_with_user_id": str(target.id),
                "permission": input_data.permission,
            },
        )

        if self._notifications:
            self._notifications.notify_project_shared(
                target_user_id=target.id,
                project_id=input_data.project_id,
                project_name=project.name,
                sharer_name=actor.full_name,
            )

        return to_share_output(share, user=target, shared_by_user=actor)


class ListProjectSharesUseCase:
    """Listar colaboradores de um projeto."""

    def __init__(
        self,
        user_repository: IUserRepository,
        project_repository: IProjectRepository,
        project_share_repository: IProjectShareRepository,
        access_policy: ProjectAccessPolicy,
    ) -> None:
        self._users = user_repository
        self._projects = project_repository
        self._shares = project_share_repository
        self._policy = access_policy

    def execute(self, *, actor_id: UUID, project_id: UUID) -> dict:
        actor = self._users.find_by_id(actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(actor_id))

        project = self._projects.find_by_id(project_id)
        if project is None:
            raise EntityNotFoundError("Projeto", str(project_id))

        is_shared = self._projects.is_shared_with_user(project_id, actor_id)
        if not self._policy.can_view(actor, project, is_shared=is_shared):
            raise AuthorizationError("Não tem acesso a este projeto")

        share_records = self._shares.find_by_project(project_id)
        items = []
        for share in share_records:
            user = self._users.find_by_id(share.user_id)
            shared_by = self._users.find_by_id(share.shared_by)
            if user and shared_by:
                items.append(to_share_output(share, user=user, shared_by_user=shared_by))

        return {"items": items, "total": len(items)}


class RemoveProjectShareUseCase:
    """Remover partilha de projeto."""

    def __init__(
        self,
        user_repository: IUserRepository,
        project_repository: IProjectRepository,
        project_share_repository: IProjectShareRepository,
        access_log_repository: IAccessLogRepository,
        access_policy: ProjectAccessPolicy,
    ) -> None:
        self._users = user_repository
        self._projects = project_repository
        self._shares = project_share_repository
        self._access_logs = access_log_repository
        self._policy = access_policy

    def execute(self, input_data: RemoveProjectShareInput) -> dict:
        actor = self._users.find_by_id(input_data.actor_id)
        if actor is None:
            raise EntityNotFoundError("Utilizador", str(input_data.actor_id))

        project = self._projects.find_by_id(input_data.project_id)
        if project is None:
            raise EntityNotFoundError("Projeto", str(input_data.project_id))

        if not self._policy.can_share(actor, project):
            raise AuthorizationError("Não tem permissão para gerir partilhas deste projeto")

        existing = self._shares.find_by_project_and_user(
            input_data.project_id, input_data.target_user_id
        )
        if existing is None:
            raise EntityNotFoundError("Partilha", str(input_data.target_user_id))

        self._shares.delete(input_data.project_id, input_data.target_user_id)

        self._access_logs.create(
            user_id=actor.id,
            action=AccessAction.PROJECT_SHARE_REMOVED,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
            metadata={
                "project_id": str(input_data.project_id),
                "removed_user_id": str(input_data.target_user_id),
            },
        )

        return {"message": "Partilha removida com sucesso"}
