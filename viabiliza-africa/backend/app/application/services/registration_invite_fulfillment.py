"""Aplica convites de registo pendentes (partilhas de projecto, etc.)."""

from __future__ import annotations

from uuid import UUID

from app.application.services.notification_service import NotificationService
from app.domain.enums.share_permission import SharePermission
from app.domain.services.share_capabilities import merge_capabilities
from app.domain.repositories.project_repository import IProjectRepository
from app.domain.repositories.project_share_repository import IProjectShareRepository
from app.domain.repositories.registration_invite_repository import (
    IRegistrationInviteRepository,
    RegistrationInvite,
)
from app.domain.repositories.user_repository import IUserRepository


class RegistrationInviteFulfillmentService:
    def __init__(
        self,
        invite_repository: IRegistrationInviteRepository,
        project_repository: IProjectRepository,
        project_share_repository: IProjectShareRepository,
        user_repository: IUserRepository,
        notification_service: NotificationService | None = None,
    ) -> None:
        self._invites = invite_repository
        self._projects = project_repository
        self._shares = project_share_repository
        self._users = user_repository
        self._notifications = notification_service

    def fulfill(self, user_id: UUID, invites: list[RegistrationInvite]) -> None:
        seen_projects: set[UUID] = set()
        for invite in invites:
            if invite.project_id and invite.project_id not in seen_projects:
                seen_projects.add(invite.project_id)
                self._apply_project_share(user_id, invite)
            self._invites.consume(invite.id, user_id)

    def _apply_project_share(self, user_id: UUID, invite: RegistrationInvite) -> None:
        project_id = invite.project_id
        if project_id is None:
            return

        project = self._projects.find_by_id(project_id)
        if project is None:
            return

        existing = self._shares.find_by_project_and_user(project_id, user_id)
        if existing:
            return

        permission = (
            invite.permission
            if SharePermission.is_valid(invite.permission)
            else SharePermission.VIEW.value
        )
        perm = SharePermission(permission)
        merged_caps = merge_capabilities(perm, invite.capabilities)
        shared_by = invite.invited_by or project.owner_id
        self._shares.create(
            project_id=project_id,
            user_id=user_id,
            shared_by=shared_by,
            permission=perm,
            office_member_id=invite.office_member_id,
            job_title=invite.job_title,
            capabilities=merged_caps,
        )

        if not self._notifications:
            return

        sharer = self._users.find_by_id(shared_by)
        sharer_name = sharer.full_name if sharer else "Analista"
        self._notifications.notify_project_shared(
            target_user_id=user_id,
            project_id=project_id,
            project_name=project.name,
            sharer_name=sharer_name,
        )
