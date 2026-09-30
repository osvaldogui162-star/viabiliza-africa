import re

from app.application.dto.auth_dto import RegisterUserInput
from app.application.mappers.user_output_mapper import user_to_output
from app.application.interfaces.password_hasher import IPasswordHasher
from app.domain.enums.access_action import AccessAction
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.domain_exceptions import (
    AuthorizationError,
    ConflictError,
    EntityNotFoundError,
    ValidationError,
)
from app.domain.repositories.access_log_repository import IAccessLogRepository
from app.domain.catalog.portal_bank_codes import validate_portal_bank_code
from app.domain.repositories.user_repository import IUserRepository

_PASSWORD_MIN_LENGTH = 8
_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class RegisterUserUseCase:
    """UC01 — Registar novo utilizador (apenas Administrador)."""

    def __init__(
        self,
        user_repository: IUserRepository,
        access_log_repository: IAccessLogRepository,
        password_hasher: IPasswordHasher,
    ) -> None:
        self._users = user_repository
        self._access_logs = access_log_repository
        self._hasher = password_hasher

    def execute(self, input_data: RegisterUserInput):
        admin = self._users.find_by_id(input_data.admin_user_id)
        if admin is None:
            raise EntityNotFoundError("Utilizador", str(input_data.admin_user_id))
        if not admin.can_manage_users():
            raise AuthorizationError("Apenas administradores podem criar utilizadores")

        email = input_data.email.strip().lower()
        self._validate(
            email,
            input_data.password,
            input_data.full_name,
            input_data.role,
            input_data.bank_code,
        )

        if self._users.find_by_email(email):
            raise ConflictError(f"Email já registado: {email}")

        role = UserRole(input_data.role)
        if role == UserRole.ADMIN:
            raise ValidationError(
                "Novos administradores devem ser promovidos por outro administrador"
            )

        bank_code: str | None = None
        if role == UserRole.BANK:
            try:
                bank_code = validate_portal_bank_code(input_data.bank_code)
            except ValueError as exc:
                raise ValidationError(str(exc)) from exc

        password_hash = self._hasher.hash(input_data.password)
        user = self._users.create(
            email=email,
            full_name=input_data.full_name.strip(),
            password_hash=password_hash,
            role=role,
            email_verified=True,
            is_active=True,
            bank_code=bank_code,
        )

        self._access_logs.create(
            user_id=admin.id,
            action=AccessAction.USER_CREATED,
            ip_address=input_data.ip_address,
            user_agent=input_data.user_agent,
            metadata={
                "created_user_id": str(user.id),
                "created_user_email": user.email,
                "role": user.role.value,
            },
        )

        return user_to_output(user)

    def _validate(
        self,
        email: str,
        password: str,
        full_name: str,
        role: str,
        bank_code: str | None,
    ) -> None:
        if not _EMAIL_PATTERN.match(email):
            raise ValidationError("Email inválido")
        if len(password) < _PASSWORD_MIN_LENGTH:
            raise ValidationError(
                f"Palavra-passe deve ter pelo menos {_PASSWORD_MIN_LENGTH} caracteres"
            )
        if not full_name.strip():
            raise ValidationError("Nome completo é obrigatório")
        if not UserRole.is_valid(role):
            raise ValidationError(
                f"Perfil inválido. Valores permitidos: {', '.join(UserRole.values())}"
            )
        if role == UserRole.BANK.value and not bank_code:
            raise ValidationError(
                "Instituição financiadora (BFA ou BDA) é obrigatória para perfil bank"
            )
