import requests
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.config import Config
from app.domain.exceptions.domain_exceptions import AuthenticationError, ValidationError


class GoogleTokenVerifier:
    """Verifica tokens Google (ID token ou authorization code)."""

    TOKEN_URL = "https://oauth2.googleapis.com/token"

    def __init__(self, config: Config) -> None:
        self._config = config

    @property
    def is_configured(self) -> bool:
        return bool(self._config.GOOGLE_CLIENT_ID and self._config.GOOGLE_CLIENT_SECRET)

    def verify_id_token(self, token: str) -> dict:
        if not self._config.GOOGLE_CLIENT_ID:
            raise ValidationError("Autenticação Google não está configurada")
        try:
            payload = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                self._config.GOOGLE_CLIENT_ID,
            )
        except ValueError as exc:
            raise AuthenticationError("Token Google inválido ou expirado") from exc

        if payload.get("iss") not in (
            "accounts.google.com",
            "https://accounts.google.com",
        ):
            raise AuthenticationError("Emissor do token Google inválido")

        return payload

    def exchange_authorization_code(self, code: str) -> dict:
        if not self.is_configured:
            raise ValidationError("Autenticação Google não está configurada")

        response = requests.post(
            self.TOKEN_URL,
            data={
                "code": code,
                "client_id": self._config.GOOGLE_CLIENT_ID,
                "client_secret": self._config.GOOGLE_CLIENT_SECRET,
                "redirect_uri": "postmessage",
                "grant_type": "authorization_code",
            },
            timeout=15,
        )
        if response.status_code >= 400:
            raise AuthenticationError("Não foi possível validar a conta Google")

        data = response.json()
        id_token_str = data.get("id_token")
        if not id_token_str:
            raise AuthenticationError("Resposta Google incompleta")

        return self.verify_id_token(id_token_str)

    @staticmethod
    def extract_profile(payload: dict) -> dict:
        google_id = payload.get("sub")
        email = (payload.get("email") or "").strip().lower()
        full_name = (payload.get("name") or email.split("@")[0] or "Utilizador").strip()
        email_verified = bool(payload.get("email_verified"))

        if not google_id:
            raise AuthenticationError("Identificador Google em falta")
        if not email:
            raise AuthenticationError("Email Google em falta")
        if not email_verified:
            raise ValidationError("O email Google deve estar verificado")

        return {
            "google_id": google_id,
            "email": email,
            "full_name": full_name[:200],
            "email_verified": email_verified,
        }
