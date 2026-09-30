"""Templates HTML transaccionais — compatíveis com clientes de email."""

from __future__ import annotations

import html
import base64

from app.infrastructure.email.brand_assets import (
    BRAND_NAME,
    BRAND_TAGLINE,
    COLOR_AMBER,
    COLOR_BORDER,
    COLOR_MUTED,
    COLOR_NAVY,
    COLOR_SURFACE,
    COLOR_TEAL,
    COLOR_TEAL_LIGHT,
    COLOR_TEXT,
    get_brand_logo_data_uri,
)


def _esc(value: str) -> str:
    return html.escape(value, quote=True)


def _icon_uri(svg: str) -> str:
    encoded = base64.b64encode(svg.strip().encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def _brand_logo_html(*, max_width: int = 220) -> str:
    logo_uri = get_brand_logo_data_uri()
    if logo_uri:
        return (
            f'<img src="{logo_uri}" width="{max_width}" alt="{_esc(BRAND_NAME)}" '
            f'style="display:block;margin:0 auto;max-width:{max_width}px;width:100%;height:auto;border:0;"/>'
        )
    return (
        f'<span style="display:inline-block;font-size:24px;font-weight:800;letter-spacing:-0.02em;'
        f'color:{COLOR_SURFACE};">'
        f'ViabilizA<span style="color:{COLOR_AMBER};">+</span> África'
        f"</span>"
    )


ICON_SHIELD = _icon_uri(
    f"""<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
    fill="none" stroke="{COLOR_TEAL}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    <path d="m9 12 2 2 4-4"/>
    </svg>"""
)

ICON_LOCK = _icon_uri(
    f"""<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
    fill="none" stroke="{COLOR_AMBER}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
    </svg>"""
)

ICON_KEY = _icon_uri(
    f"""<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
    fill="none" stroke="{COLOR_SURFACE}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="8" cy="15" r="4"/>
    <path d="m10.5 12.5 8-8"/>
    <path d="m18 2 4 4"/>
    <path d="m14 6 4 4"/>
    </svg>"""
)

ICON_MAIL = _icon_uri(
    """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24"
    fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="2" y="4" width="20" height="16" rx="2"/>
    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
    </svg>"""
)

GRADIENT_BAR = (
    f"linear-gradient(90deg,{COLOR_NAVY} 0%,{COLOR_TEAL} 35%,{COLOR_AMBER} 68%,{COLOR_TEAL_LIGHT} 100%)"
)
GRADIENT_CTA = (
    f"linear-gradient(118deg,{COLOR_NAVY} 0%,{COLOR_TEAL} 38%,{COLOR_AMBER} 100%)"
)
GRADIENT_HEADER = (
    f"linear-gradient(145deg,{COLOR_NAVY} 0%,#023048 42%,{COLOR_TEAL} 100%)"
)


def render_signup_otp_email(
    *,
    full_name: str,
    otp_code: str,
    expires_minutes: int,
) -> tuple[str, str]:
    """Retorna (text/plain, text/html) para email OTP de registo."""
    safe_name = _esc(full_name.strip() or "Utilizador")
    safe_otp = _esc(otp_code)
    digits = " ".join(safe_otp)

    text_body = (
        f"Olá {full_name.strip() or 'Utilizador'},\n\n"
        f"Obrigado por escolher {BRAND_NAME}.\n"
        f"Utilize este código OTP para concluir o registo e verificar a sua conta:\n\n"
        f"  {otp_code}\n\n"
        f"Válido por {expires_minutes} minutos.\n\n"
        f"Nunca partilhe este código com ninguém, mesmo que alguém se identifique como {BRAND_NAME}.\n\n"
        f"Cumprimentos,\n"
        f"Equipa {BRAND_NAME}\n"
    )

    html_body = f"""<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Código de verificação — {BRAND_NAME}</title>
</head>
<body style="margin:0;padding:0;background:linear-gradient(165deg,#eef8f4 0%,#f8fafc 45%,#f3faf7 100%);background-color:#f4f6f8;font-family:'Segoe UI',Roboto,Arial,sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:linear-gradient(165deg,#eef8f4 0%,#f8fafc 45%,#f3faf7 100%);background-color:#f4f6f8;padding:32px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width:520px;background:#ffffff;border-radius:16px;overflow:hidden;border:1px solid #e5e7eb;box-shadow:0 18px 48px -24px rgba(10,26,46,0.28);">
          <!-- Barra gradiente superior -->
          <tr>
            <td style="height:5px;background:linear-gradient(90deg,#059669 0%,#0a1a2e 55%,#c6a43f 100%);background-color:#059669;font-size:0;line-height:0;">&nbsp;</td>
          </tr>
          <tr>
            <td style="padding:28px 32px 8px 32px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td align="center" style="padding-bottom:18px;border-bottom:1px solid #e5e7eb;">
                    <span style="display:inline-block;font-size:22px;font-weight:800;letter-spacing:-0.02em;background:linear-gradient(135deg,#059669 0%,#0a1a2e 70%,#c6a43f 100%);-webkit-background-clip:text;background-clip:text;color:#059669;">
                      ViabilizA<span style="color:#c6a43f;">+</span> África
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Corpo -->
          <tr>
            <td style="padding:24px 32px 8px 32px;color:#374151;font-size:15px;line-height:1.65;">
              <p style="margin:0 0 16px 0;font-size:16px;color:#111827;">
                Olá <strong>{safe_name}</strong>,
              </p>
              <p style="margin:0 0 14px 0;">
                Obrigado por escolher <strong>{BRAND_NAME}</strong>.
                Utilize este código OTP para concluir o registo e verificar a sua conta.
              </p>
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin:0 0 18px 0;background:linear-gradient(135deg,#fffbeb 0%,#fef3c7 100%);background-color:#fffbeb;border-radius:12px;border:1px solid #fde68a;">
                <tr>
                  <td style="padding:12px 14px;">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                      <tr>
                        <td style="vertical-align:top;padding-right:10px;">
                          <img src="{ICON_LOCK}" width="18" height="18" alt="" style="display:block;border:0;"/>
                        </td>
                        <td style="font-size:13px;color:#92400e;line-height:1.5;">
                          Nunca partilhe este código com ninguém, mesmo que alguém se identifique como
                          <strong>{BRAND_NAME}</strong>.
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- OTP -->
          <tr>
            <td align="center" style="padding:8px 32px 28px 32px;">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin:0 auto;">
                <tr>
                  <td align="center" style="padding-bottom:10px;">
                    <img src="{ICON_MAIL}" width="22" height="22" alt="" style="display:inline-block;border:0;vertical-align:middle;opacity:0.9;"/>
                    <span style="display:inline-block;margin-left:8px;font-size:12px;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:#6b7280;vertical-align:middle;">
                      Código de verificação
                    </span>
                  </td>
                </tr>
                <tr>
                  <td align="center" style="border-radius:14px;background:linear-gradient(135deg,#0a1a2e 0%,#1a3a5c 55%,#059669 100%);background-color:#0a1a2e;padding:18px 36px;box-shadow:0 12px 28px -12px rgba(10,26,46,0.55);">
                    <span style="font-family:'Courier New',Consolas,monospace;font-size:32px;font-weight:800;letter-spacing:0.35em;color:#ffffff;text-shadow:0 1px 2px rgba(0,0,0,0.2);">
                      {digits}
                    </span>
                  </td>
                </tr>
                <tr>
                  <td align="center" style="padding-top:14px;font-size:13px;color:#6b7280;">
                    Expira em <strong style="color:#059669;">{expires_minutes} minutos</strong>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Rodapé -->
          <tr>
            <td style="padding:20px 32px 28px 32px;border-top:1px solid #e5e7eb;">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td style="vertical-align:top;padding-right:10px;">
                    <img src="{ICON_SHIELD}" width="20" height="20" alt="" style="display:block;border:0;"/>
                  </td>
                  <td style="font-size:14px;color:#4b5563;line-height:1.55;">
                    Cumprimentos,<br/>
                    <strong style="color:#111827;">Equipa {BRAND_NAME}</strong>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="height:4px;background:linear-gradient(90deg,#c6a43f 0%,#059669 50%,#0a1a2e 100%);background-color:#059669;font-size:0;line-height:0;">&nbsp;</td>
          </tr>
        </table>
        <p style="margin:18px 0 0 0;font-size:11px;color:#9ca3af;text-align:center;max-width:520px;">
          Se não solicitou este registo, ignore este email. A sua conta não será criada sem o código.
        </p>
      </td>
    </tr>
  </table>
</body>
</html>"""

    return text_body, html_body


def render_password_reset_email(
    *,
    full_name: str,
    reset_url: str,
    expires_hours: int,
) -> tuple[str, str]:
    """Retorna (text/plain, text/html) para email de recuperação de palavra-passe."""
    safe_name = _esc(full_name.strip() or "Utilizador")
    safe_url = _esc(reset_url)
    logo_html = _brand_logo_html(max_width=200)

    text_body = (
        f"Olá {full_name.strip() or 'Utilizador'},\n\n"
        f"Recebemos um pedido para redefinir a palavra-passe da sua conta {BRAND_NAME}.\n\n"
        f"Aceda ao link seguro abaixo para escolher uma nova palavra-passe:\n\n"
        f"  {reset_url}\n\n"
        f"Este link expira em {expires_hours} horas.\n\n"
        f"Se não solicitou esta alteração, ignore este email — a sua palavra-passe permanece inalterada.\n\n"
        f"Cumprimentos,\n"
        f"Equipa {BRAND_NAME}\n"
    )

    html_body = f"""<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <meta http-equiv="X-UA-Compatible" content="IE=edge"/>
  <title>Recuperação de palavra-passe — {BRAND_NAME}</title>
</head>
<body style="margin:0;padding:0;background-color:#eef4f6;font-family:'Segoe UI',Roboto,Arial,sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:linear-gradient(165deg,#e8f4f5 0%,#f4f7fa 48%,#eef6f8 100%);background-color:#eef4f6;padding:36px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width:560px;background:{COLOR_SURFACE};border-radius:20px;overflow:hidden;border:1px solid {COLOR_BORDER};box-shadow:0 22px 56px -28px rgba(1,22,54,0.35);">
          <!-- Barra gradiente superior -->
          <tr>
            <td style="height:6px;background:{GRADIENT_BAR};background-color:{COLOR_TEAL};font-size:0;line-height:0;">&nbsp;</td>
          </tr>
          <!-- Cabeçalho com logotipo -->
          <tr>
            <td align="center" style="padding:28px 36px 24px 36px;background:{GRADIENT_HEADER};background-color:{COLOR_NAVY};">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin:0 auto;background:{COLOR_SURFACE};border-radius:14px;box-shadow:0 10px 28px -12px rgba(0,0,0,0.35);">
                <tr>
                  <td align="center" style="padding:18px 28px 14px 28px;">
                    {logo_html}
                  </td>
                </tr>
              </table>
              <p style="margin:16px 0 0 0;font-size:13px;line-height:1.55;color:rgba(255,255,255,0.88);letter-spacing:0.02em;text-align:center;max-width:360px;">
                {BRAND_TAGLINE}
              </p>
            </td>
          </tr>
          <!-- Ícone + título -->
          <tr>
            <td align="center" style="padding:28px 36px 8px 36px;">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin:0 auto;">
                <tr>
                  <td align="center" style="width:52px;height:52px;border-radius:14px;background:{GRADIENT_CTA};background-color:{COLOR_TEAL};">
                    <img src="{ICON_KEY}" width="22" height="22" alt="" style="display:block;margin:15px auto;border:0;"/>
                  </td>
                </tr>
              </table>
              <p style="margin:18px 0 0 0;font-size:22px;font-weight:800;color:{COLOR_TEXT};letter-spacing:-0.02em;text-align:center;">
                Recuperação de palavra-passe
              </p>
              <p style="margin:8px 0 0 0;font-size:14px;color:{COLOR_MUTED};text-align:center;line-height:1.55;">
                Pedido seguro para redefinir o acesso à sua conta
              </p>
            </td>
          </tr>
          <!-- Corpo -->
          <tr>
            <td style="padding:20px 36px 8px 36px;color:#374151;font-size:15px;line-height:1.7;">
              <p style="margin:0 0 14px 0;font-size:16px;color:{COLOR_TEXT};">
                Olá <strong>{safe_name}</strong>,
              </p>
              <p style="margin:0 0 18px 0;">
                Recebemos um pedido para redefinir a palavra-passe da sua conta
                <strong style="color:{COLOR_TEAL};">{BRAND_NAME}</strong>.
                Clique no botão abaixo para escolher uma nova palavra-passe.
              </p>
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin:0 0 22px 0;background:linear-gradient(135deg,#fff8eb 0%,#fff4d6 100%);background-color:#fff8eb;border-radius:12px;border:1px solid #fde68a;">
                <tr>
                  <td style="padding:14px 16px;">
                    <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                      <tr>
                        <td style="vertical-align:top;padding-right:10px;">
                          <img src="{ICON_LOCK}" width="18" height="18" alt="" style="display:block;border:0;"/>
                        </td>
                        <td style="font-size:13px;color:#92400e;line-height:1.55;">
                          Se não solicitou esta alteração, ignore este email.
                          A sua palavra-passe <strong>permanece inalterada</strong>.
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- CTA -->
          <tr>
            <td align="center" style="padding:8px 36px 24px 36px;">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin:0 auto;">
                <tr>
                  <td align="center" bgcolor="{COLOR_TEAL}" style="border-radius:12px;background:{GRADIENT_CTA};background-color:{COLOR_TEAL};box-shadow:0 14px 32px -14px rgba(1,22,54,0.55);">
                    <a href="{safe_url}" target="_blank" style="display:inline-block;padding:16px 36px;font-size:16px;font-weight:700;color:#ffffff;text-decoration:none;border-radius:12px;letter-spacing:0.01em;">
                      Redefinir palavra-passe
                    </a>
                  </td>
                </tr>
              </table>
              <p style="margin:18px 0 0 0;font-size:13px;color:{COLOR_MUTED};text-align:center;line-height:1.55;">
                Este link expira em
                <strong style="color:{COLOR_TEAL};">{expires_hours} horas</strong>
              </p>
            </td>
          </tr>
          <!-- Link alternativo -->
          <tr>
            <td style="padding:0 36px 24px 36px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background:#f9fafb;border-radius:10px;border:1px solid {COLOR_BORDER};">
                <tr>
                  <td style="padding:14px 16px;font-size:12px;color:{COLOR_MUTED};line-height:1.6;text-align:center;">
                    Se o botão não funcionar, copie e cole este endereço no browser:<br/>
                    <a href="{safe_url}" style="color:{COLOR_TEAL};word-break:break-all;text-decoration:underline;">{safe_url}</a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <!-- Rodapé -->
          <tr>
            <td style="padding:22px 36px 28px 36px;border-top:1px solid {COLOR_BORDER};">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td style="vertical-align:top;padding-right:10px;">
                    <img src="{ICON_SHIELD}" width="20" height="20" alt="" style="display:block;border:0;"/>
                  </td>
                  <td style="font-size:14px;color:#4b5563;line-height:1.55;">
                    Cumprimentos,<br/>
                    <strong style="color:{COLOR_TEXT};">Equipa {BRAND_NAME}</strong>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="height:5px;background:{GRADIENT_BAR};background-color:{COLOR_TEAL};font-size:0;line-height:0;">&nbsp;</td>
          </tr>
        </table>
        <p style="margin:20px 0 0 0;font-size:11px;color:#9ca3af;text-align:center;max-width:560px;line-height:1.5;">
          Email automático de segurança. Por favor não responda a esta mensagem.
        </p>
      </td>
    </tr>
  </table>
</body>
</html>"""

    return text_body, html_body
