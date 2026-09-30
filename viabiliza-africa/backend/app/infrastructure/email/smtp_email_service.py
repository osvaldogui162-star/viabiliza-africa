import logging
import smtplib
import threading
import time
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, parseaddr

from app.application.interfaces.email_service import IEmailService
from app.application.services.integration_config_service import IntegrationConfigService
from app.config import Config
from app.domain.exceptions.domain_exceptions import ValidationError
from app.infrastructure.email.templates import render_password_reset_email, render_signup_otp_email

logger = logging.getLogger(__name__)

SMTP_TIMEOUT_SECONDS = 12
_DEFAULT_FROM_NAME = "ViabilizA+ África"

_PLACEHOLDER_SMTP_VALUES = frozenset({"...", "changeme", "your_smtp_host", "smtp.example.com"})


def _is_usable_smtp_host(host: str) -> bool:
    """Rejeita hosts vazios, placeholders (.env) ou malformados (evita UnicodeEncodeError IDNA)."""
    normalized = (host or "").strip().lower()
    if not normalized or normalized in _PLACEHOLDER_SMTP_VALUES:
        return False
    if normalized.startswith(".") or normalized.endswith(".") or ".." in normalized:
        return False
    if not any(ch.isalnum() for ch in normalized):
        return False
    return True


def _normalize_smtp_credentials(
    host: str | None,
    user: str | None,
    password: str | None,
) -> tuple[str, str, str]:
    h = (host or "").strip()
    u = (user or "").strip()
    p = password or ""
    if u in _PLACEHOLDER_SMTP_VALUES or u == "...":
        u = ""
    if p in _PLACEHOLDER_SMTP_VALUES or p == "...":
        p = ""
    if not _is_usable_smtp_host(h):
        h = ""
    return h, u, p


def _build_from_addresses(settings: dict, fallback_from: str) -> tuple[str, str]:
    """
    Devolve (header From, envelope MAIL FROM).

    Gmail (e a maioria dos relays) rejeita ou bloqueia entregas quando o envelope
    difere da conta autenticada — ex.: From noreply@outro-dominio.com com login @gmail.com.
    """
    user = (settings.get("user") or "").strip()
    from_raw = (settings.get("from") or fallback_from or "").strip()
    display_name, from_addr = parseaddr(from_raw)
    if not display_name:
        display_name = _DEFAULT_FROM_NAME

    host = (settings.get("host") or "").lower()
    is_gmail = "gmail.com" in host or (user.endswith("@gmail.com") if user else False)

    if user and (is_gmail or not from_addr or from_addr.lower() != user.lower()):
        header_from = formataddr((display_name, user))
        envelope_from = user
        return header_from, envelope_from

    addr = from_addr or user
    header_from = formataddr((display_name, addr)) if addr else from_raw
    envelope_from = addr or user or from_raw
    return header_from, envelope_from


class SmtpEmailService(IEmailService):
    """Serviço de e-mail SMTP (env + integrações admin) com anexo PDF."""

    def __init__(
        self,
        config: Config,
        integration_config: IntegrationConfigService | None = None,
    ) -> None:
        self._config = config
        self._integrations = integration_config
        self._settings_cache: dict | None = None
        self._settings_cached_at = 0.0

    def _smtp_settings(self) -> dict:
        env_host, env_user, env_password = _normalize_smtp_credentials(
            self._config.SMTP_HOST,
            self._config.SMTP_USER,
            self._config.SMTP_PASSWORD,
        )
        if env_host:
            return {
                "host": env_host,
                "port": self._config.SMTP_PORT,
                "user": env_user,
                "password": env_password,
                "from": self._config.SMTP_FROM,
                "use_tls": self._config.SMTP_USE_TLS,
            }

        now = time.monotonic()
        if self._settings_cache is not None and (now - self._settings_cached_at) < 60:
            return self._settings_cache

        if self._integrations is not None:
            raw = self._integrations.get_smtp_config()
            host, user, password = _normalize_smtp_credentials(
                raw.get("host"),
                raw.get("user"),
                raw.get("password"),
            )
            settings = {
                **raw,
                "host": host,
                "user": user,
                "password": password,
            }
        else:
            settings = {
                "host": "",
                "port": self._config.SMTP_PORT,
                "user": "",
                "password": "",
                "from": self._config.SMTP_FROM,
                "use_tls": self._config.SMTP_USE_TLS,
            }
        self._settings_cache = settings
        self._settings_cached_at = now
        return settings

    def _send(self, *, to_email: str, subject: str, message: MIMEMultipart) -> bool:
        settings = self._smtp_settings()
        host = (settings.get("host") or "").strip()
        if not host:
            logger.warning(
                "SMTP não configurado — email simulado para %s | assunto=%s",
                to_email,
                subject,
            )
            return False

        from_addr = settings.get("from") or self._config.SMTP_FROM
        header_from, envelope_from = _build_from_addresses(settings, from_addr)
        message["Subject"] = subject
        message["From"] = header_from
        message["To"] = to_email
        if settings.get("user"):
            message["Reply-To"] = settings["user"]

        port = int(settings.get("port") or 587)
        use_tls = bool(settings.get("use_tls", True))
        user = (settings.get("user") or "").strip()
        password = settings.get("password") or ""

        try:
            with smtplib.SMTP(host, port, timeout=SMTP_TIMEOUT_SECONDS) as server:
                server.ehlo()
                if use_tls:
                    server.starttls()
                    server.ehlo()
                if user:
                    server.login(user, password)
                server.sendmail(envelope_from, [to_email], message.as_string())
        except (smtplib.SMTPException, OSError, TimeoutError, UnicodeEncodeError) as exc:
            logger.exception(
                "Falha SMTP ao enviar para %s (envelope=%s, header_from=%s)",
                to_email,
                envelope_from,
                header_from,
            )
            raise ValidationError(
                f"Não foi possível enviar o email (SMTP): {exc}. "
                "Verifique SMTP_HOST/USER/PASSWORD ou a ligação à internet."
            ) from exc

        logger.info(
            "Email enviado para %s | assunto=%s | envelope=%s",
            to_email,
            subject,
            envelope_from,
        )
        return True

    def send_password_reset(self, to_email: str, reset_url: str, full_name: str) -> None:
        subject = "ViabilizA+ África — Recuperação de palavra-passe"
        text_body, html_body = render_password_reset_email(
            full_name=full_name,
            reset_url=reset_url,
            expires_hours=self._config.PASSWORD_RESET_TOKEN_EXPIRES_HOURS,
        )

        message = MIMEMultipart("alternative")
        message.attach(MIMEText(text_body, "plain", "utf-8"))
        message.attach(MIMEText(html_body, "html", "utf-8"))
        self._send(to_email=to_email, subject=subject, message=message)

    def send_signup_otp(
        self, to_email: str, full_name: str, otp_code: str, expires_minutes: int
    ) -> bool:
        subject = "ViabilizA+ África — Código de verificação"
        text_body, html_body = render_signup_otp_email(
            full_name=full_name,
            otp_code=otp_code,
            expires_minutes=expires_minutes,
        )

        message = MIMEMultipart("alternative")
        message.attach(MIMEText(text_body, "plain", "utf-8"))
        message.attach(MIMEText(html_body, "html", "utf-8"))
        try:
            sent = self._send(to_email=to_email, subject=subject, message=message)
        except ValidationError:
            logger.warning(
                "OTP signup — falha SMTP para %s; código=%s (modo simulado)",
                to_email,
                otp_code,
            )
            return False
        if not sent:
            logger.warning(
                "OTP signup simulado para %s — código=%s (SMTP não configurado)",
                to_email,
                otp_code,
            )
        return sent

    def send_report_email(
        self,
        to_email: str,
        *,
        subject: str,
        body_html: str,
        body_text: str,
        pdf_bytes: bytes,
        filename: str,
    ) -> None:
        message = MIMEMultipart("mixed")

        alt = MIMEMultipart("alternative")
        alt.attach(MIMEText(body_text, "plain", "utf-8"))
        alt.attach(MIMEText(body_html, "html", "utf-8"))
        message.attach(alt)

        attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
        attachment.add_header("Content-Disposition", "attachment", filename=filename)
        message.attach(attachment)

        sent = self._send(to_email=to_email, subject=subject, message=message)
        if not sent:
            logger.warning(
                "Relatório PDF (%s bytes) não enviado por SMTP — modo simulado para %s",
                len(pdf_bytes),
                to_email,
            )

    def send_report_email_async(
        self,
        to_email: str,
        *,
        subject: str,
        body_html: str,
        body_text: str,
        pdf_bytes: bytes,
        filename: str,
        on_error=None,
    ) -> None:
        """Envia em background para a API responder de imediato."""

        def _worker() -> None:
            try:
                self.send_report_email(
                    to_email,
                    subject=subject,
                    body_html=body_html,
                    body_text=body_text,
                    pdf_bytes=pdf_bytes,
                    filename=filename,
                )
            except Exception as exc:  # noqa: BLE001
                logger.exception("Envio assíncrono de relatório falhou para %s", to_email)
                if on_error is not None:
                    on_error(exc)

        threading.Thread(
            target=_worker,
            name=f"smtp-report-{to_email[:24]}",
            daemon=True,
        ).start()
