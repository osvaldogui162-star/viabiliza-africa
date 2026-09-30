from flask import Flask, jsonify
from httpx import HTTPError, RemoteProtocolError
from marshmallow import ValidationError as MarshmallowValidationError
from postgrest.exceptions import APIError as PostgrestAPIError

from app.domain.exceptions.domain_exceptions import (
    AccountPendingApprovalError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DomainException,
    EntityNotFoundError,
    ValidationError,
)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(DomainException)
    def handle_domain_exception(exc: DomainException):
        status_map = {
            EntityNotFoundError: 404,
            AuthenticationError: 401,
            AuthorizationError: 403,
            AccountPendingApprovalError: 403,
            ValidationError: 400,
            ConflictError: 409,
        }
        status = status_map.get(type(exc), 400)
        payload: dict = {"code": exc.code, "message": exc.message}
        if isinstance(exc, AccountPendingApprovalError):
            payload["email"] = exc.email
        return jsonify({"error": payload}), status

    @app.errorhandler(RemoteProtocolError)
    @app.errorhandler(HTTPError)
    def handle_http_transport_error(exc: Exception):
        return jsonify(
            {
                "error": {
                    "code": "database_unavailable",
                    "message": "Falha temporária na ligação à base de dados. Tente novamente.",
                }
            }
        ), 503

    @app.errorhandler(PostgrestAPIError)
    def handle_postgrest_error(exc: PostgrestAPIError):
        message = exc.message or "Erro na base de dados"
        if exc.code == "PGRST205":
            message = (
                "Tabela não encontrada no Supabase. "
                "Execute as migrations em migrations/supabase/ no SQL Editor."
            )
        return jsonify(
            {"error": {"code": "database_error", "message": message, "details": exc.details}}
        ), 500

    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow_validation(exc: MarshmallowValidationError):
        return jsonify(
            {
                "error": {
                    "code": "validation_error",
                    "message": "Dados inválidos",
                    "details": exc.messages,
                }
            }
        ), 400

    @app.errorhandler(404)
    def handle_not_found(_exc):
        return jsonify(
            {"error": {"code": "not_found", "message": "Recurso não encontrado"}}
        ), 404

    @app.errorhandler(500)
    def handle_internal_error(_exc):
        return jsonify(
            {"error": {"code": "internal_error", "message": "Erro interno do servidor"}}
        ), 500
