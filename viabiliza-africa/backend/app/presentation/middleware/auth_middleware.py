from flask import Flask, g, request

from app.application.interfaces.token_service import ITokenService
from app.domain.exceptions.domain_exceptions import AuthenticationError
from app.domain.repositories.user_repository import IUserRepository


PUBLIC_PATHS = {
    "/api/v1/terminal/billing/sync",
    "/api/v1/auth/login",
    "/api/v1/auth/signup/request-otp",
    "/api/v1/auth/signup/verify-otp",
    "/api/v1/auth/signup/resend-otp",
    "/api/v1/auth/recover-password",
    "/api/v1/auth/reset-password",
    "/api/v1/auth/refresh",
    "/health",
}


def register_auth_middleware(
    app: Flask,
    token_service: ITokenService,
    user_repository: IUserRepository,
) -> None:
    @app.before_request
    def load_current_user() -> None:
        g.current_user = None

        if (
            request.path in PUBLIC_PATHS
            or request.path.startswith("/api/v1/verify/")
            or request.path.startswith("/api/v1/reports/share/")
            or request.method == "OPTIONS"
        ):
            return

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return

        token = auth_header.removeprefix("Bearer ").strip()
        if not token:
            return

        try:
            payload = token_service.decode_access_token(token)
            user = user_repository.find_by_id(payload.user_id)
            if user and user.is_active:
                g.current_user = user
        except AuthenticationError:
            g.current_user = None
