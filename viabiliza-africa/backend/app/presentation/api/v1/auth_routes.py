from flask import Blueprint, g, jsonify, request
from marshmallow import ValidationError as MarshmallowValidationError

from app.application.dto.auth_dto import (
    GoogleAuthInput,
    LoginInput,
    PasswordRecoveryInput,
    RefreshTokenInput,
    RegisterUserInput,
    ResetPasswordInput,
    SignupOtpRequestInput,
    SignupOtpResendInput,
    SignupOtpVerifyInput,
    UpdateUserPreferencesInput,
)
from app.di.container import Container
from app.presentation.decorators.rbac import require_auth, require_roles
from app.presentation.schemas.auth_schemas import (
    LoginSchema,
    LogoutSchema,
    PasswordRecoverySchema,
    RefreshTokenSchema,
    RegisterUserSchema,
    ResetPasswordSchema,
    SignupOtpRequestSchema,
    SignupOtpResendSchema,
    SignupOtpVerifySchema,
    UpdateUserPreferencesSchema,
    GoogleAuthSchema,
)
from app.presentation.serializers import to_dict
from app.domain.enums.user_role import UserRole


auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


def _client_meta() -> dict:
    return {
        "ip_address": request.headers.get("X-Forwarded-For", request.remote_addr),
        "user_agent": request.headers.get("User-Agent"),
    }


@auth_bp.post("/login")
def login():
    """UC02 — Fazer login."""
    try:
        data = LoginSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = auth_bp.container  # type: ignore[attr-defined]
    result = container.login_use_case.execute(
        LoginInput(
            email=data["email"],
            password=data["password"],
            **_client_meta(),
        )
    )
    return jsonify(to_dict(result)), 200


@auth_bp.get("/registration/config")
def registration_config():
    """Configuração pública de registo (modo, termos)."""
    container: Container = auth_bp.container  # type: ignore[attr-defined]
    return jsonify(container.registration_policy_service.public_config()), 200


@auth_bp.get("/registration/status")
def registration_status():
    """Estado de aprovação — polling em tempo real (página pending-approval)."""
    email = (request.args.get("email") or "").strip()
    if not email:
        return jsonify(
            {"error": {"code": "validation_error", "message": "Email em falta"}}
        ), 400

    container: Container = auth_bp.container  # type: ignore[attr-defined]
    result = container.get_registration_status_use_case.execute(
        email=email,
        ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
    )
    return jsonify(result), 200


@auth_bp.get("/google/config")
def google_auth_config():
    """Configuração pública para o botão Google no frontend."""
    container: Container = auth_bp.container  # type: ignore[attr-defined]
    config = container.config
    enabled = bool(config.GOOGLE_CLIENT_ID and config.GOOGLE_CLIENT_SECRET)
    return jsonify(
        {
            "enabled": enabled,
            "client_id": config.GOOGLE_CLIENT_ID if enabled else None,
        }
    ), 200


@auth_bp.post("/google")
def google_auth():
    """Login ou registo via Google OAuth."""
    try:
        data = GoogleAuthSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    if not data.get("credential") and not data.get("code"):
        return jsonify(
            {"error": {"code": "validation_error", "message": "Credencial Google em falta"}}
        ), 400

    container: Container = auth_bp.container  # type: ignore[attr-defined]
    result, is_new_user = container.google_auth_use_case.execute(
        GoogleAuthInput(
            credential=data.get("credential"),
            code=data.get("code"),
            terms_accepted=bool(data.get("terms_accepted")),
            terms_version=data.get("terms_version"),
            **_client_meta(),
        )
    )
    payload = to_dict(result)
    payload["is_new_user"] = is_new_user
    return jsonify(payload), 201 if is_new_user else 200


@auth_bp.post("/signup/request-otp")
def request_signup_otp():
    """Registo público — envia código OTP por email."""
    try:
        data = SignupOtpRequestSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = auth_bp.container  # type: ignore[attr-defined]
    result = container.request_signup_otp_use_case.execute(
        SignupOtpRequestInput(
            email=data["email"],
            password=data["password"],
            full_name=data["full_name"],
            terms_accepted=bool(data.get("terms_accepted")),
            terms_version=data.get("terms_version"),
            **_client_meta(),
        )
    )
    return jsonify(result), 200


@auth_bp.post("/signup/verify-otp")
def verify_signup_otp():
    """Registo público — valida OTP, cria conta e inicia sessão."""
    try:
        data = SignupOtpVerifySchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = auth_bp.container  # type: ignore[attr-defined]
    result = container.verify_signup_otp_use_case.execute(
        SignupOtpVerifyInput(
            email=data["email"],
            code=data["code"],
            terms_accepted=bool(data.get("terms_accepted")),
            terms_version=data.get("terms_version"),
            **_client_meta(),
        )
    )
    return jsonify(to_dict(result)), 201


@auth_bp.post("/signup/resend-otp")
def resend_signup_otp():
    """Reenvia código OTP de registo."""
    try:
        data = SignupOtpResendSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = auth_bp.container  # type: ignore[attr-defined]
    result = container.resend_signup_otp_use_case.execute(
        SignupOtpResendInput(email=data["email"], **_client_meta())
    )
    return jsonify(result), 200


@auth_bp.post("/register")
@require_roles(UserRole.ADMIN)
def register_user():
    """UC01 — Registar novo utilizador (Administrador)."""
    try:
        data = RegisterUserSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = auth_bp.container  # type: ignore[attr-defined]
    result = container.register_user_use_case.execute(
        RegisterUserInput(
            email=data["email"],
            password=data["password"],
            full_name=data["full_name"],
            role=data["role"],
            bank_code=data.get("bank_code"),
            admin_user_id=g.current_user.id,
            **_client_meta(),
        )
    )
    return jsonify(to_dict(result)), 201


@auth_bp.post("/recover-password")
def recover_password():
    """UC03 — Solicitar recuperação de palavra-passe."""
    try:
        data = PasswordRecoverySchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = auth_bp.container  # type: ignore[attr-defined]
    result = container.recover_password_use_case.execute(
        PasswordRecoveryInput(email=data["email"], **_client_meta())
    )
    return jsonify(result), 200


@auth_bp.post("/reset-password")
def reset_password():
    """UC03 — Redefinir palavra-passe com token."""
    try:
        data = ResetPasswordSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = auth_bp.container  # type: ignore[attr-defined]
    result = container.reset_password_use_case.execute(
        ResetPasswordInput(
            token=data["token"],
            new_password=data["new_password"],
            **_client_meta(),
        )
    )
    return jsonify(result), 200


@auth_bp.post("/refresh")
def refresh_token():
    """Renovar access token."""
    try:
        data = RefreshTokenSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = auth_bp.container  # type: ignore[attr-defined]
    result = container.refresh_token_use_case.execute(
        RefreshTokenInput(refresh_token=data["refresh_token"], **_client_meta())
    )
    return jsonify(to_dict(result)), 200


@auth_bp.post("/logout")
@require_auth
def logout():
    """Terminar sessão e revogar refresh token."""
    try:
        data = LogoutSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = auth_bp.container  # type: ignore[attr-defined]
    result = container.logout_use_case.execute(
        user_id=g.current_user.id,
        refresh_token=data.get("refresh_token"),
        **_client_meta(),
    )
    return jsonify(result), 200


@auth_bp.get("/me")
@require_auth
def get_current_user():
    """Perfil do utilizador autenticado."""
    container: Container = auth_bp.container  # type: ignore[attr-defined]
    result = container.get_current_user_use_case.execute(g.current_user.id)
    return jsonify(to_dict(result)), 200


@auth_bp.patch("/me/preferences")
@require_auth
def update_user_preferences():
    """Actualizar preferências do utilizador (moeda de exibição)."""
    try:
        data = UpdateUserPreferencesSchema().load(request.get_json() or {})
    except MarshmallowValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "details": exc.messages}}), 400

    container: Container = auth_bp.container  # type: ignore[attr-defined]
    result = container.update_user_preferences_use_case.execute(
        UpdateUserPreferencesInput(
            user_id=g.current_user.id,
            preferred_currency=data["preferred_currency"],
            **_client_meta(),
        )
    )
    return jsonify(to_dict(result)), 200
