import os
import socket
from dataclasses import dataclass, field


def detect_lan_ip() -> str:
    """Detecta o IPv4 da máquina na rede local (para QR Codes / telemóvel)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.connect(("8.8.8.8", 80))
            return sock.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def resolve_frontend_base_url() -> str:
    """
    FRONTEND_BASE_URL=auto → http://{IP_LAN}:3000
    Evita QR Codes com IP antigo/errado (ex.: .105 quando o PC é .185).
    """
    raw = (os.getenv("FRONTEND_BASE_URL") or "auto").strip()
    if not raw or raw.lower() == "auto":
        return f"http://{detect_lan_ip()}:3000"
    return raw.rstrip("/")


@dataclass(frozen=True)
class Config:
    """Configuração centralizada da aplicação (Single Responsibility)."""

    SECRET_KEY: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "dev-secret-key"))
    FLASK_ENV: str = field(default_factory=lambda: os.getenv("FLASK_ENV", "development"))
    DEBUG: bool = field(
        default_factory=lambda: os.getenv("FLASK_DEBUG", "False").lower() == "true"
    )

    SUPABASE_URL: str = field(
        default_factory=lambda: os.getenv("SUPABASE_URL", "").strip()
    )
    SUPABASE_SERVICE_ROLE_KEY: str = field(
        default_factory=lambda: os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    )

    JWT_SECRET_KEY: str = field(
        default_factory=lambda: os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "jwt-dev"))
    )
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES: int = field(
        default_factory=lambda: int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60"))
    )
    JWT_REFRESH_TOKEN_EXPIRES_DAYS: int = field(
        default_factory=lambda: int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "7"))
    )
    JWT_ALGORITHM: str = "HS256"

    PASSWORD_RESET_TOKEN_EXPIRES_HOURS: int = field(
        default_factory=lambda: int(os.getenv("PASSWORD_RESET_TOKEN_EXPIRES_HOURS", "24"))
    )
    SIGNUP_OTP_EXPIRES_MINUTES: int = field(
        default_factory=lambda: int(os.getenv("SIGNUP_OTP_EXPIRES_MINUTES", "10"))
    )
    SIGNUP_OTP_MAX_ATTEMPTS: int = field(
        default_factory=lambda: int(os.getenv("SIGNUP_OTP_MAX_ATTEMPTS", "5"))
    )
    SIGNUP_OTP_RESEND_COOLDOWN_SECONDS: int = field(
        default_factory=lambda: int(os.getenv("SIGNUP_OTP_RESEND_COOLDOWN_SECONDS", "60"))
    )
    FRONTEND_RESET_PASSWORD_URL: str = field(
        default_factory=lambda: os.getenv(
            "FRONTEND_RESET_PASSWORD_URL", "http://localhost:3000/reset-password"
        )
    )

    SMTP_HOST: str = field(default_factory=lambda: os.getenv("SMTP_HOST", ""))
    SMTP_PORT: int = field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    SMTP_USER: str = field(default_factory=lambda: os.getenv("SMTP_USER", ""))
    SMTP_PASSWORD: str = field(default_factory=lambda: os.getenv("SMTP_PASSWORD", ""))
    SMTP_FROM: str = field(
        default_factory=lambda: os.getenv(
            "SMTP_FROM", "ViabilizA+ África <noreply@viabiliza.africa>"
        )
    )
    SMTP_USE_TLS: bool = field(
        default_factory=lambda: os.getenv("SMTP_USE_TLS", "True").lower() == "true"
    )

    VERIFICATION_BASE_URL: str = field(
        default_factory=lambda: os.getenv("VERIFICATION_BASE_URL", "http://localhost:5000")
    )
    FRONTEND_BASE_URL: str = field(default_factory=resolve_frontend_base_url)

    CORS_ORIGINS: list[str] = field(default_factory=list)

    # Kanban externo (Trello)
    KANBAN_PROVIDER: str = field(
        default_factory=lambda: os.getenv("KANBAN_PROVIDER", "local").strip().lower()
    )
    TRELLO_API_KEY: str = field(
        default_factory=lambda: os.getenv("TRELLO_API_KEY", "").strip()
    )
    TRELLO_API_TOKEN: str = field(
        default_factory=lambda: os.getenv("TRELLO_API_TOKEN", "").strip()
    )

    # APIs bancárias (Módulo 6 — UC34)
    BFA_API_URL: str = field(default_factory=lambda: os.getenv("BFA_API_URL", "").strip())
    BFA_API_KEY: str = field(default_factory=lambda: os.getenv("BFA_API_KEY", "").strip())
    BDA_API_URL: str = field(default_factory=lambda: os.getenv("BDA_API_URL", "").strip())
    BDA_API_KEY: str = field(default_factory=lambda: os.getenv("BDA_API_KEY", "").strip())

    REPORT_SHARE_BASE_URL: str = field(
        default_factory=lambda: os.getenv(
            "REPORT_SHARE_BASE_URL", "http://localhost:5000/api/v1/reports/share"
        )
    )
    WHATSAPP_SHARE_BASE_URL: str = field(
        default_factory=lambda: os.getenv(
            "WHATSAPP_SHARE_BASE_URL", "https://wa.me/?text="
        )
    )
    REPORT_SHARE_DAYS: int = field(
        default_factory=lambda: int(os.getenv("REPORT_SHARE_DAYS", "7"))
    )

    GOOGLE_MAPS_API_KEY: str = field(
        default_factory=lambda: os.getenv("GOOGLE_MAPS_API_KEY", "").strip()
    )

    GOOGLE_CLIENT_ID: str = field(
        default_factory=lambda: os.getenv("GOOGLE_CLIENT_ID", "").strip()
    )
    GOOGLE_CLIENT_SECRET: str = field(
        default_factory=lambda: os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
    )

    REGISTRATION_MODE: str = field(
        default_factory=lambda: os.getenv("REGISTRATION_MODE", "admin_approval").strip()
    )
    TERMS_VERSION: str = field(
        default_factory=lambda: os.getenv("TERMS_VERSION", "2026-01").strip()
    )
    AUTH_RATE_LIMIT_MAX: int = field(
        default_factory=lambda: int(os.getenv("AUTH_RATE_LIMIT_MAX", "12"))
    )
    AUTH_RATE_LIMIT_WINDOW_SECONDS: int = field(
        default_factory=lambda: int(os.getenv("AUTH_RATE_LIMIT_WINDOW_SECONDS", "900"))
    )

    ANGOLA_API_BASE_URL: str = field(
        default_factory=lambda: os.getenv(
            "ANGOLA_API_BASE_URL", "https://angolaapi.onrender.com/api/v1"
        ).strip()
    )

    # AppyPay (TST)
    APPYPAY_CLIENT_ID: str = field(
        default_factory=lambda: os.getenv("APPYPAY_CLIENT_ID", "").strip()
    )
    APPYPAY_CLIENT_SECRET: str = field(
        default_factory=lambda: os.getenv("APPYPAY_CLIENT_SECRET", "").strip()
    )
    APPYPAY_RESOURCE: str = field(
        default_factory=lambda: os.getenv(
            "APPYPAY_RESOURCE", "2aed7612-de64-46b5-9e59-1f48f8902d14"
        ).strip()
    )
    APPYPAY_GPO_METHOD: str = field(
        default_factory=lambda: os.getenv(
            "APPYPAY_GPO_METHOD", "GPO_84a04402-6a55-42b5-84db-eb499816a5fb"
        ).strip()
    )
    APPYPAY_REF_METHOD: str = field(
        default_factory=lambda: os.getenv(
            "APPYPAY_REF_METHOD", "REF_ecd68875-54b1-406f-adac-260bbc35ccc3"
        ).strip()
    )
    APPYPAY_API_BASE: str = field(
        default_factory=lambda: os.getenv(
            "APPYPAY_API_BASE", "https://gwy-api-tst.appypay.co.ao/v2.0"
        ).strip()
    )
    APPYPAY_SANDBOX: bool = field(
        default_factory=lambda: os.getenv("APPYPAY_SANDBOX", "true").lower() == "true"
    )

    def __post_init__(self) -> None:
        origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
        parsed = [o.strip() for o in origins.split(",") if o.strip()]
        frontend = self.FRONTEND_BASE_URL.rstrip("/")
        if frontend and frontend not in parsed:
            parsed.append(frontend)
        # Garante localhost mesmo quando FRONTEND_BASE_URL é o IP LAN
        for extra in ("http://localhost:3000", "http://127.0.0.1:3000"):
            if extra not in parsed:
                parsed.append(extra)
        object.__setattr__(self, "CORS_ORIGINS", parsed)

    def validate(self) -> None:
        missing = []
        if not self.SUPABASE_URL:
            missing.append("SUPABASE_URL")
        if not self.SUPABASE_SERVICE_ROLE_KEY:
            missing.append("SUPABASE_SERVICE_ROLE_KEY")
        if missing:
            raise ValueError(f"Variáveis de ambiente obrigatórias em falta: {', '.join(missing)}")


def get_config() -> Config:
    return Config()
