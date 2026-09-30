from abc import ABC, abstractmethod


class IEmailService(ABC):
    """Contrato para envio de emails transacionais."""

    @abstractmethod
    def send_password_reset(self, to_email: str, reset_url: str, full_name: str) -> None:
        ...

    @abstractmethod
    def send_signup_otp(
        self, to_email: str, full_name: str, otp_code: str, expires_minutes: int
    ) -> bool:
        """Envia OTP de registo. Retorna True se enviado via SMTP."""
        ...

    @abstractmethod
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
        ...
