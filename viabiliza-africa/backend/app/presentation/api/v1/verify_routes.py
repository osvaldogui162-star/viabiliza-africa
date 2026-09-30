from flask import Blueprint, jsonify

from app.di.container import Container
from app.domain.exceptions.domain_exceptions import EntityNotFoundError, ValidationError


verify_bp = Blueprint("verify", __name__, url_prefix="/api/v1/verify")


@verify_bp.get("/budget/<verification_hash>")
def verify_budget(verification_hash: str):
    """Verificação pública de orçamento (QR Code)."""
    container: Container = verify_bp.container  # type: ignore[attr-defined]
    try:
        result = container.verify_budget_use_case.execute(verification_hash)
        return jsonify(result), 200
    except ValidationError as exc:
        return jsonify({"valid": False, "message": str(exc)}), 404


@verify_bp.get("/report/<verification_hash>")
def verify_report(verification_hash: str):
    """Verificação pública de relatório (QR Code)."""
    container: Container = verify_bp.container  # type: ignore[attr-defined]
    try:
        result = container.verify_report_use_case.execute(verification_hash)
        return jsonify(result), 200
    except EntityNotFoundError:
        return jsonify(
            {"valid": False, "message": "Relatório não encontrado ou foi alterado"}
        ), 404
