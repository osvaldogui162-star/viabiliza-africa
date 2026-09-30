import hashlib
import json

from app.application.interfaces.hash_service import IHashService


class Sha256HashService(IHashService):
    """Hashing SHA-256 para rastreabilidade de dados."""

    def hash_dict(self, data: dict) -> str:
        canonical = json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        return self.hash_string(canonical)

    def hash_string(self, value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def hash_chain(self, *hashes: str) -> str:
        return self.hash_string("|".join(hashes))
