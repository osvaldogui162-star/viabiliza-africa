from abc import ABC, abstractmethod


class IHashService(ABC):
    """Contrato para hashing SHA-256 de dados rastreáveis."""

    @abstractmethod
    def hash_dict(self, data: dict) -> str:
        ...

    @abstractmethod
    def hash_string(self, value: str) -> str:
        ...

    @abstractmethod
    def hash_chain(self, *hashes: str) -> str:
        ...
