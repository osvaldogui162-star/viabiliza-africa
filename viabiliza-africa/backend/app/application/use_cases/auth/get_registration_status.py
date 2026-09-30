"""Consulta pública do estado de aprovação (polling em tempo real)."""

from app.domain.exceptions.domain_exceptions import ValidationError
from app.domain.repositories.user_repository import IUserRepository
from app.infrastructure.auth.auth_rate_limiter import AuthRateLimiter


class GetRegistrationStatusUseCase:
    def __init__(
        self,
        user_repository: IUserRepository,
        rate_limiter: AuthRateLimiter,
    ) -> None:
        self._users = user_repository
        self._rate_limiter = rate_limiter

    def execute(self, *, email: str, ip_address: str | None = None) -> dict:
        normalized = email.strip().lower()
        if not normalized or "@" not in normalized:
            raise ValidationError("Email inválido")

        self._rate_limiter.check("reg_status", normalized)
        if ip_address:
            self._rate_limiter.check("reg_status_ip", ip_address)

        user = self._users.find_by_email(normalized)
        if user is None:
            return {"status": "unknown", "can_sign_in": False}

        if user.is_active:
            return {
                "status": "active",
                "can_sign_in": True,
                "role": user.role.value,
            }

        return {"status": "pending_approval", "can_sign_in": False}
