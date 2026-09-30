from app.application.dto.auth_dto import UserOutput
from app.domain.entities.user import User


def user_to_output(user: User) -> UserOutput:
    return UserOutput(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value,
        is_active=user.is_active,
        preferred_currency=user.preferred_currency,
        bank_code=user.bank_code,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )
