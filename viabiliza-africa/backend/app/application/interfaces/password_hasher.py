from abc import ABC, abstractmethod


class IPasswordHasher(ABC):
    """Contrato para hashing de palavras-passe (Strategy Pattern)."""

    @abstractmethod
    def hash(self, password: str) -> str:
        ...

    @abstractmethod
    def verify(self, password: str, password_hash: str) -> bool:
        ...
