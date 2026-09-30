import bcrypt

from app.application.interfaces.password_hasher import IPasswordHasher


class BcryptPasswordHasher(IPasswordHasher):
    """Hashing de palavras-passe com bcrypt (Strategy Pattern)."""

    def hash(self, password: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify(self, password: str, password_hash: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
