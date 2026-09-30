from functools import wraps
from typing import Callable

from flask import g, jsonify

from app.domain.enums.user_role import UserRole
from app.domain.exceptions.domain_exceptions import AuthenticationError, AuthorizationError


def require_auth(fn: Callable):
    """Decorator que exige utilizador autenticado."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not getattr(g, "current_user", None):
            return _error_response(AuthenticationError("Token de autenticação em falta"), 401)
        return fn(*args, **kwargs)

    return wrapper


def require_roles(*roles: UserRole):
    """Decorator RBAC — exige um dos perfis indicados."""

    def decorator(fn: Callable):
        @wraps(fn)
        @require_auth
        def wrapper(*args, **kwargs):
            current = g.current_user
            if current.role not in roles:
                return _error_response(
                    AuthorizationError("Não tem permissão para esta operação"),
                    403,
                )
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def _error_response(exc: Exception, status: int):
    code = getattr(exc, "code", "error")
    message = getattr(exc, "message", str(exc))
    return jsonify({"error": {"code": code, "message": message}}), status
