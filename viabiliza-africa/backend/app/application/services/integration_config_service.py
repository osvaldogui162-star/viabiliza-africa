from app.config import Config
from app.domain.enums.integration_key import IntegrationKey
from app.domain.repositories.admin_config_repository import IIntegrationSettingsRepository


SECRET_KEYS = {"api_key", "password", "api_token"}


def mask_settings(settings: dict) -> dict:
    """Oculta segredos nas respostas da API."""
    masked = {}
    for key, value in settings.items():
        if key in SECRET_KEYS and value:
            masked[key] = f"****{str(value)[-4:]}" if len(str(value)) > 4 else "****"
        else:
            masked[key] = value
    return masked


class IntegrationConfigService:
    """Lê integrações da BD com fallback para variáveis de ambiente."""

    def __init__(
        self,
        repository: IIntegrationSettingsRepository,
        config: Config,
    ) -> None:
        self._repo = repository
        self._config = config
        self._cache: dict[str, dict] = {}

    def invalidate_cache(self) -> None:
        self._cache.clear()

    def get_settings(self, key: IntegrationKey, *, masked: bool = False) -> dict:
        if key.value in self._cache and not masked:
            settings = self._cache[key.value]
        else:
            settings = self._resolve(key)
            if not masked:
                self._cache[key.value] = settings
        return mask_settings(settings) if masked else settings

    def get_bfa_config(self) -> tuple[str, str]:
        s = self.get_settings(IntegrationKey.BFA)
        return s.get("api_url") or self._config.BFA_API_URL, s.get("api_key") or self._config.BFA_API_KEY

    def get_bda_config(self) -> tuple[str, str]:
        s = self.get_settings(IntegrationKey.BDA)
        return s.get("api_url") or self._config.BDA_API_URL, s.get("api_key") or self._config.BDA_API_KEY

    def get_smtp_config(self) -> dict:
        s = self.get_settings(IntegrationKey.SMTP)
        return {
            "host": s.get("host") or self._config.SMTP_HOST,
            "port": int(s.get("port") or self._config.SMTP_PORT),
            "user": s.get("user") or self._config.SMTP_USER,
            "password": s.get("password") or self._config.SMTP_PASSWORD,
            "from": s.get("from") or self._config.SMTP_FROM,
            "use_tls": s.get("use_tls", self._config.SMTP_USE_TLS),
        }

    def get_trello_config(self) -> tuple[str, str]:
        s = self.get_settings(IntegrationKey.TRELLO)
        return s.get("api_key") or self._config.TRELLO_API_KEY, s.get("api_token") or self._config.TRELLO_API_TOKEN

    def is_active(self, key: IntegrationKey) -> bool:
        row = self._repo.find_by_key(key)
        return row.is_active if row else True

    def _resolve(self, key: IntegrationKey) -> dict:
        row = self._repo.find_by_key(key)
        if row and row.is_active:
            return dict(row.settings)
        return self._env_defaults(key)

    def _env_defaults(self, key: IntegrationKey) -> dict:
        if key == IntegrationKey.BFA:
            return {"api_url": self._config.BFA_API_URL, "api_key": self._config.BFA_API_KEY}
        if key == IntegrationKey.BDA:
            return {"api_url": self._config.BDA_API_URL, "api_key": self._config.BDA_API_KEY}
        if key == IntegrationKey.SMTP:
            return {
                "host": self._config.SMTP_HOST,
                "port": self._config.SMTP_PORT,
                "user": self._config.SMTP_USER,
                "password": self._config.SMTP_PASSWORD,
                "from": self._config.SMTP_FROM,
                "use_tls": self._config.SMTP_USE_TLS,
            }
        return {
            "api_key": self._config.TRELLO_API_KEY,
            "api_token": self._config.TRELLO_API_TOKEN,
        }
