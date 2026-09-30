import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from app.application.interfaces.token_service import ITokenService, TokenPayload
from app.config import Config
from app.domain.exceptions.domain_exceptions import AuthenticationError


class JwtTokenService(ITokenService):
    """Geração e validação de tokens JWT."""

    def __init__(self, config: Config) -> None:
        self._config = config

    def create_access_token(self, payload: TokenPayload) -> str:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=self._config.JWT_ACCESS_TOKEN_EXPIRES_MINUTES)
        claims = {
            "sub": str(payload.user_id),
            "email": payload.email,
            "role": payload.role,
            "iat": now,
            "exp": expires,
            "type": "access",
        }
        return jwt.encode(
            claims,
            self._config.JWT_SECRET_KEY,
            algorithm=self._config.JWT_ALGORITHM,
        )

    def create_refresh_token(self) -> str:
        return secrets.token_urlsafe(48)

    def decode_access_token(self, token: str) -> TokenPayload:
        try:
            claims = jwt.decode(
                token,
                self._config.JWT_SECRET_KEY,
                algorithms=[self._config.JWT_ALGORITHM],
            )
            if claims.get("type") != "access":
                raise AuthenticationError("Token inválido")
            return TokenPayload(
                user_id=UUID(claims["sub"]),
                email=claims["email"],
                role=claims["role"],
            )
        except jwt.ExpiredSignatureError as exc:
            raise AuthenticationError("Token expirado") from exc
        except jwt.InvalidTokenError as exc:
            raise AuthenticationError("Token inválido") from exc

    def hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def get_access_token_expires_seconds(self) -> int:
        return self._config.JWT_ACCESS_TOKEN_EXPIRES_MINUTES * 60
