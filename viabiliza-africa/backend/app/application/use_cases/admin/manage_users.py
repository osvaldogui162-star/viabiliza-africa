from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.application.dto.auth_dto import (
    ApproveUserInput,
    ExtendUserAccessInput,
    UpdateUserInput,
    UpdateUserRoleInput,
    UserOutput,
)
from app.application.mappers.user_output_mapper import user_to_output
from app.application.services.notification_service import NotificationService
from app.application.use_cases.admin.mappers import to_subscription_output
from app.domain.enums.access_action import AccessAction
from app.domain.enums.subscription_status import SubscriptionStatus
from app.domain.enums.user_role import UserRole
from app.domain.repositories.admin_config_repository import ISubscriptionRepository
from app.domain.exceptions.domain_exceptions import (
    AuthorizationError,
    EntityNotFoundError,
    ValidationError,
)
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.catalog.portal_bank_codes import validate_portal_bank_code
from app.domain.repositories.user_repository import IUserRepository


def _bank_code_for_role(role: UserRole, bank_code: str | None, *, existing: str | None) -> str | None:
    if role == UserRole.BANK:
        try:
            return validate_portal_bank_code(bank_code or existing)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
    if bank_code is not None:
        return validate_portal_bank_code(bank_code) if bank_code else None
    return None if role != UserRole.BANK else existing

class ListUsersUseCase:
    """Listar utilizadores (apenas Administrador)."""

    def __init__(self, user_repository: IUserRepository) -> None:
        self._users = user_repository

    def execute(
        self,
        *,
        admin_user_id: UUID,
        role: str | None = None,
        is_active: bool | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        admin = self._require_admin(admin_user_id)
        _ = admin

        parsed_role = UserRole(role) if role else None
        users = self._users.find_all(
            role=parsed_role,
            is_active=is_active,
            limit=limit,
            offset=offset,
        )
        total = self._users.count(role=parsed_role, is_active=is_active)

        return {
            "items": [self._to_output(u) for u in users],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def _require_admin(self, admin_user_id: UUID):
        admin = self._users.find_by_id(admin_user_id)
        if admin is None:
            raise EntityNotFoundError("Utilizador", str(admin_user_id))
        if not admin.can_manage_users():
            raise AuthorizationError()
        return admin

    @staticmethod
    def _to_output(user) -> UserOutput:
        return user_to_output(user)


class GetUserUseCase:
    """Obter detalhes de um utilizador (apenas Administrador)."""

    def __init__(self, user_repository: IUserRepository) -> None:
        self._users = user_repository

    def execute(self, *, admin_user_id: UUID, target_user_id: UUID) -> UserOutput:
        admin = self._users.find_by_id(admin_user_id)
        if admin is None or not admin.can_manage_users():
            raise AuthorizationError()

        user = self._users.find_by_id(target_user_id)
        if user is None:
            raise EntityNotFoundError("Utilizador", str(target_user_id))

        return user_to_output(user)


class UpdateUserRoleUseCase:
    """UC04 — Atribuir ou revogar permissões (perfil de acesso)."""

    def __init__(
        self,
        user_repository: IUserRepository,
        access_log_repository: IAccessLogRepository,
    ) -> None:
        self._users = user_repository
        self._access_logs = access_log_repository

    def execute(self, input_data: UpdateUserRoleInput) -> UserOutput:
        admin = self._users.find_by_id(input_data.admin_user_id)
        if admin is None or not admin.can_manage_users():
            raise AuthorizationError()

        if not UserRole.is_valid(input_data.role):
            raise ValidationError(
                f"Perfil inválido. Valores permitidos: {', '.join(UserRole.values())}"
            )

        target = self._users.find_by_id(input_data.target_user_id)
        if target is None:
            raise EntityNotFoundError("Utilizador", str(input_data.target_user_id))

        if target.id == admin.id and input_data.role != UserRole.ADMIN.value:
            raise ValidationError("Não pode remover o seu próprio perfil de administrador")

        new_role = UserRole(input_data.role)
        old_role = target.role.value

        resolved_bank = _bank_code_for_role(
            new_role,
            input_data.bank_code,
            existing=target.bank_code,
        )
        user = self._users.update(
            target.id,
            role=new_role,
            bank_code="" if new_role != UserRole.BANK else resolved_bank,
        )

        self._access_logs.create(
            user_id=admin.id,
            action=AccessAction.ROLE_CHANGED,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
            metadata={
                "target_user_id": str(target.id),
                "old_role": old_role,
                "new_role": new_role.value,
            },
        )

        return user_to_output(user)


class UpdateUserUseCase:
    """UC04 — Editar utilizador (nome, perfil, estado activo)."""

    def __init__(
        self,
        user_repository: IUserRepository,
        access_log_repository: IAccessLogRepository,
        subscription_repository: ISubscriptionRepository | None = None,
    ) -> None:
        self._users = user_repository
        self._access_logs = access_log_repository
        self._subs_repo = subscription_repository

    def execute(self, input_data: UpdateUserInput) -> UserOutput:
        admin = self._users.find_by_id(input_data.admin_user_id)
        if admin is None or not admin.can_manage_users():
            raise AuthorizationError()

        target = self._users.find_by_id(input_data.target_user_id)
        if target is None:
            raise EntityNotFoundError("Utilizador", str(input_data.target_user_id))

        new_role = None
        if input_data.role is not None:
            if not UserRole.is_valid(input_data.role):
                raise ValidationError(
                    f"Perfil inválido. Valores permitidos: {', '.join(UserRole.values())}"
                )
            if target.id == admin.id and input_data.role != UserRole.ADMIN.value:
                raise ValidationError("Não pode remover o seu próprio perfil de administrador")
            new_role = UserRole(input_data.role)

        if input_data.is_active is False and target.id == admin.id:
            raise ValidationError("Não pode desactivar a sua própria conta")

        effective_role = new_role or target.role
        bank_update: str | None | object = ...
        if input_data.bank_code is not None or new_role is not None:
            resolved = _bank_code_for_role(
                effective_role,
                input_data.bank_code,
                existing=target.bank_code,
            )
            bank_update = resolved if effective_role == UserRole.BANK else None

        update_kwargs: dict = {
            "full_name": input_data.full_name,
            "role": new_role,
            "is_active": input_data.is_active,
        }
        if bank_update is not ...:
            update_kwargs["bank_code"] = bank_update

        user = self._users.update(target.id, **update_kwargs)

        if (
            self._subs_repo
            and input_data.is_active is True
            and not target.is_active
            and user.role == UserRole.FINANCIAL
        ):
            # Aprovação com plano/prazo deve usar ApproveUserUseCase
            pass

        action = (
            AccessAction.USER_DEACTIVATED
            if input_data.is_active is False
            else AccessAction.USER_UPDATED
        )

        self._access_logs.create(
            user_id=admin.id,
            action=action,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
            metadata={
                "target_user_id": str(target.id),
                "changes": {
                    k: v
                    for k, v in {
                        "full_name": input_data.full_name,
                        "role": input_data.role,
                        "is_active": input_data.is_active,
                    }.items()
                    if v is not None
                },
            },
        )

        return user_to_output(user)


class ApproveUserUseCase:
    """Aprovar registo pendente — activar conta, plano e prazo definidos pelo admin."""

    def __init__(
        self,
        user_repository: IUserRepository,
        subscription_repository: ISubscriptionRepository,
        access_log_repository: IAccessLogRepository,
        notification_service: NotificationService,
    ) -> None:
        self._users = user_repository
        self._subs = subscription_repository
        self._access_logs = access_log_repository
        self._notifications = notification_service

    def execute(self, input_data: ApproveUserInput) -> dict:
        admin = self._users.find_by_id(input_data.admin_user_id)
        if admin is None or not admin.can_manage_users():
            raise AuthorizationError()

        target = self._users.find_by_id(input_data.target_user_id)
        if target is None:
            raise EntityNotFoundError("Utilizador", str(input_data.target_user_id))

        role = UserRole(input_data.role) if input_data.role else target.role
        if role == UserRole.ADMIN:
            raise ValidationError("Não pode aprovar utilizadores como administrador")

        if role == UserRole.FINANCIAL:
            if not input_data.plan_id:
                raise ValidationError("Seleccione o plano para analistas financeiros")
            if not input_data.access_days or input_data.access_days < 1:
                raise ValidationError("Indique a duração de acesso em dias (mínimo 1)")
            if self._subs.find_plan_by_id(input_data.plan_id) is None:
                raise EntityNotFoundError("Plano", str(input_data.plan_id))

        user = self._users.update(
            target.id,
            role=role if input_data.role else None,
            is_active=True,
        )

        subscription_output = None
        ends_at = None
        if role == UserRole.FINANCIAL and input_data.plan_id and input_data.access_days:
            ends_at = datetime.now(timezone.utc) + timedelta(days=input_data.access_days)
            sub = self._subs.assign_subscription(
                user_id=user.id,
                plan_id=input_data.plan_id,
                status=SubscriptionStatus.ACTIVE,
                ends_at=ends_at,
                created_by=admin.id,
            )
            plan = self._subs.find_plan_by_id(input_data.plan_id)
            subscription_output = to_subscription_output(sub, plan, user=user)

        self._notifications.notify_user_access_granted(
            user_id=user.id,
            plan_name=subscription_output["plan"]["name"] if subscription_output else None,
            ends_at=ends_at,
            approved=True,
        )

        self._access_logs.create(
            user_id=admin.id,
            action=AccessAction.USER_APPROVED,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
            metadata={
                "target_user_id": str(user.id),
                "role": user.role.value,
                "plan_id": str(input_data.plan_id) if input_data.plan_id else None,
                "access_days": input_data.access_days,
                "ends_at": ends_at.isoformat() if ends_at else None,
            },
        )

        return {
            "user": user_to_output(user),
            "subscription": subscription_output,
            "message": "Utilizador aprovado com sucesso",
        }


class ExtendUserAccessUseCase:
    """Renovar ou alterar plano/prazo de um analista activo."""

    def __init__(
        self,
        user_repository: IUserRepository,
        subscription_repository: ISubscriptionRepository,
        access_log_repository: IAccessLogRepository,
        notification_service: NotificationService,
    ) -> None:
        self._users = user_repository
        self._subs = subscription_repository
        self._access_logs = access_log_repository
        self._notifications = notification_service

    def execute(self, input_data: ExtendUserAccessInput) -> dict:
        admin = self._users.find_by_id(input_data.admin_user_id)
        if admin is None or not admin.can_manage_users():
            raise AuthorizationError()

        target = self._users.find_by_id(input_data.target_user_id)
        if target is None:
            raise EntityNotFoundError("Utilizador", str(input_data.target_user_id))

        if target.role != UserRole.FINANCIAL:
            raise ValidationError("Extensão de plano aplica-se apenas a analistas financeiros")

        if input_data.access_days < 1:
            raise ValidationError("Duração mínima: 1 dia")

        plan = self._subs.find_plan_by_id(input_data.plan_id)
        if plan is None:
            raise EntityNotFoundError("Plano", str(input_data.plan_id))

        ends_at = datetime.now(timezone.utc) + timedelta(days=input_data.access_days)
        sub = self._subs.assign_subscription(
            user_id=target.id,
            plan_id=input_data.plan_id,
            status=SubscriptionStatus.ACTIVE,
            ends_at=ends_at,
            created_by=admin.id,
        )

        if not target.is_active:
            self._users.update(target.id, is_active=True)

        subscription_output = to_subscription_output(sub, plan, user=target)

        self._notifications.notify_user_access_granted(
            user_id=target.id,
            plan_name=plan.name,
            ends_at=ends_at,
            approved=False,
        )

        self._access_logs.create(
            user_id=admin.id,
            action=AccessAction.USER_ACCESS_EXTENDED,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
            metadata={
                "target_user_id": str(target.id),
                "plan_id": str(input_data.plan_id),
                "access_days": input_data.access_days,
                "ends_at": ends_at.isoformat(),
            },
        )

        return {
            "subscription": subscription_output,
            "message": "Acesso actualizado com sucesso",
        }
