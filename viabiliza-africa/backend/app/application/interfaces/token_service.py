from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600


@dataclass(frozen=True)
class TokenPayload:
    user_id: UUID
    email: str
    role: str


class ITokenService(ABC):
    """Contrato para geração e validação de tokens JWT."""

    @abstractmethod
    def create_access_token(self, payload: TokenPayload) -> str:
        ...

    @abstractmethod
    def create_refresh_token(self) -> str:
        ...

    @abstractmethod
    def decode_access_token(self, token: str) -> TokenPayload:
        ...

    @abstractmethod
    def hash_token(self, token: str) -> str:
        ...

    @abstractmethod
    def get_access_token_expires_seconds(self) -> int:
        ...
