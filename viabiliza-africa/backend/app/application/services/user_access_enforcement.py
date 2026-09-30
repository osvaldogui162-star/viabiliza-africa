"""Garante bloqueio quando subscrição com prazo expira."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from app.domain.enums.subscription_status import SubscriptionStatus
from app.domain.enums.user_role import UserRole
from app.domain.entities.user import User
from app.domain.exceptions.domain_exceptions import AuthenticationError
from app.domain.repositories.admin_config_repository import ISubscriptionRepository
from app.domain.repositories.user_repository import IUserRepository


class UserAccessEnforcementService:
    def __init__(
        self,
        user_repository: IUserRepository,
        subscription_repository: ISubscriptionRepository,
    ) -> None:
        self._users = user_repository
        self._subs = subscription_repository

    def enforce(self, user: User) -> User:
        if user.role == UserRole.ADMIN:
            return user

        if not user.is_active:
            raise AuthenticationError(
                "Conta inactiva ou aguarda aprovação. Contacte o administrador."
            )

        if user.role == UserRole.USER:
            return user

        if user.role == UserRole.BANK:
            if not user.bank_code:
                raise AuthenticationError(
                    "Conta de instituição incompleta. Contacte o administrador ViabilizA+."
                )
            return user

        active = self._subs.find_active_subscription(user.id)
        if active:
            return user

        now = datetime.now(timezone.utc)
        subs = self._subs.find_subscriptions(user_id=user.id, limit=20)
        had_timed_access = any(s.ends_at is not None for s in subs)
        timed_expired = any(
            s.ends_at is not None
            and s.ends_at < now
            and s.status in (SubscriptionStatus.EXPIRED, SubscriptionStatus.ACTIVE)
            for s in subs
        )

        if had_timed_access and timed_expired:
            for s in subs:
                if s.ends_at and s.ends_at < now and s.status == SubscriptionStatus.ACTIVE:
                    self._subs.update_subscription_status(s.id, SubscriptionStatus.EXPIRED)
            self._users.update(user.id, is_active=False)
            raise AuthenticationError(
                "O prazo de acesso expirou. Contacte o administrador para renovação."
            )

        return user
