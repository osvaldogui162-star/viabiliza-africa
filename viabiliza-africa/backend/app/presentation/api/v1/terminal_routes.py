from flask import Blueprint, jsonify, request

from app.di.container import Container

terminal_bp = Blueprint("terminal", __name__)


def _extract_api_key() -> str | None:
    header = request.headers.get("X-Terminal-Api-Key", "").strip()
    if header:
        return header
    auth = request.headers.get("Authorization", "").strip()
    if auth.startswith("Bearer "):
        token = auth.removeprefix("Bearer ").strip()
        if token.startswith("vza_"):
            return token
    return None


@terminal_bp.post("/api/v1/terminal/billing/sync")
def sync_billing_via_api_key():
    """Sync ERP/facturação — autenticação via API Key do projecto (sem JWT)."""
    raw_key = _extract_api_key()
    if not raw_key:
        return jsonify({"error": {"code": "missing_api_key", "message": "X-Terminal-Api-Key em falta"}}), 401

    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return jsonify({"error": {"code": "validation_error", "message": "JSON inválido"}}), 400

    container: Container = terminal_bp.container  # type: ignore[attr-defined]
    try:
        result = container.sync_billing_via_api_key_use_case.execute(api_key=raw_key, payload=payload)
    except Exception as exc:
        from app.domain.exceptions.domain_exceptions import AuthenticationError, ValidationError

        if isinstance(exc, AuthenticationError):
            return jsonify({"error": {"code": "invalid_api_key", "message": str(exc)}}), 401
        if isinstance(exc, ValidationError):
            return jsonify({"error": {"code": "validation_error", "message": str(exc)}}), 400
        raise

    return jsonify(result), 200
