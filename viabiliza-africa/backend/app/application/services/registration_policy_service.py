"""Política de registo self-service — convites, aprovação admin e termos."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.config import Config
from app.domain.enums.registration_mode import RegistrationMode
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.domain_exceptions import AuthorizationError, ValidationError
from app.domain.repositories.registration_invite_repository import (
    IRegistrationInviteRepository,
    RegistrationInvite,
)


@dataclass(frozen=True)
class RegistrationDecision:
    role: UserRole
    is_active: bool
    requires_admin_notification: bool
    invites: list[RegistrationInvite]
    assign_free_plan: bool


class RegistrationPolicyService:
    CURRENT_TERMS_VERSION = "2026-01"

    def __init__(
        self,
        config: Config,
        invite_repository: IRegistrationInviteRepository,
    ) -> None:
        self._config = config
        self._invites = invite_repository

    @property
    def mode(self) -> RegistrationMode:
        return RegistrationMode.parse(getattr(self._config, "REGISTRATION_MODE", None))

    @property
    def terms_version(self) -> str:
        return getattr(self._config, "TERMS_VERSION", None) or self.CURRENT_TERMS_VERSION

    def public_config(self) -> dict:
        return {
            "mode": self.mode.value,
            "terms_version": self.terms_version,
            "require_terms": True,
        }

    def validate_terms(self, *, terms_accepted: bool, terms_version: str | None) -> None:
        if not terms_accepted:
            raise ValidationError(
                "Deve aceitar os Termos de Utilização e a Política de Privacidade."
            )
        if terms_version and terms_version != self.terms_version:
            raise ValidationError(
                "Versão dos termos desactualizada. Actualize a página e aceite novamente."
            )

    def decide_new_user(self, email: str) -> RegistrationDecision:
        pending = self._invites.find_pending_for_email(email)
        mode = self.mode

        if mode == RegistrationMode.INVITE_ONLY and not pending:
            raise AuthorizationError(
                "Registo apenas por convite. Peça a um analista ou administrador para o convidar."
            )

        if pending:
            # Colaborador convidado para projecto
            role = UserRole.USER if any(i.role == "user" for i in pending) else UserRole.FINANCIAL
            if any(i.role == "financial" for i in pending):
                role = UserRole.FINANCIAL
        else:
            role = UserRole.FINANCIAL

        requires_approval = mode == RegistrationMode.ADMIN_APPROVAL
        is_active = not requires_approval
        assign_plan = role == UserRole.FINANCIAL and is_active

        return RegistrationDecision(
            role=role,
            is_active=is_active,
            requires_admin_notification=requires_approval or True,
            invites=pending,
            assign_free_plan=assign_plan,
        )

    def create_project_invite(
        self,
        *,
        email: str,
        invited_by: UUID,
        project_id: UUID,
        permission: str,
        capabilities: dict | None = None,
        office_member_id: UUID | None = None,
        job_title: str | None = None,
    ) -> RegistrationInvite:
        expires = datetime.now(timezone.utc) + timedelta(days=30)
        return self._invites.upsert_pending_project_share(
            email=email.lower(),
            invited_by=invited_by,
            project_id=project_id,
            permission=permission,
            expires_at=expires,
            capabilities=capabilities,
            office_member_id=office_member_id,
            job_title=job_title,
        )

    def consume_invites(self, invites: list[RegistrationInvite], user_id: UUID) -> None:
        for inv in invites:
            self._invites.consume(inv.id, user_id)
