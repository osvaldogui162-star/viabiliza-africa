from flask import Blueprint, g, jsonify, request

from app.di.container import Container
from app.domain.exceptions.domain_exceptions import ValidationError
from app.presentation.decorators.rbac import require_auth


automation_bp = Blueprint("automation", __name__, url_prefix="/api/v1")


@automation_bp.get("/companies/nif/<string:nif>")
@require_auth
def lookup_company_nif(nif: str):
    """Consulta dados reais da empresa no portal AGT/MINFIN."""
    container: Container = automation_bp.container  # type: ignore[attr-defined]
    result = container.lookup_company_by_nif_use_case.execute(nif)
    return jsonify(result), 200


@automation_bp.post("/companies/extract-document")
@require_auth
def extract_company_document():
    """Extrair NIF, nome e contactos de PDF/TXT para auto-preencher empresa."""
    if "file" not in request.files:
        return jsonify({"error": {"code": "validation_error", "message": "Ficheiro em falta"}}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": {"code": "validation_error", "message": "Nome de ficheiro inválido"}}), 400
    lower = file.filename.lower()
    if not lower.endswith((".pdf", ".txt")):
        return jsonify({"error": {"code": "validation_error", "message": "Formato deve ser PDF ou TXT"}}), 400

    container: Container = automation_bp.container  # type: ignore[attr-defined]
    try:
        result = container.extract_company_document_use_case.execute(
            file_bytes=file.read(),
            filename=file.filename,
        )
    except ValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "message": str(exc)}}), 400
    return jsonify(result), 200


@automation_bp.get("/banks")
@require_auth
def list_financing_banks():
    container: Container = automation_bp.container  # type: ignore[attr-defined]
    return jsonify(container.list_financing_banks_use_case.execute()), 200


@automation_bp.get("/validate/bi/<string:bi>")
@require_auth
def validate_bi(bi: str):
    """Valida Bilhete de Identidade angolano via Angola API."""
    container: Container = automation_bp.container  # type: ignore[attr-defined]
    try:
        result = container.validate_angola_bi_use_case.execute(bi)
    except ValidationError as exc:
        return jsonify({"valid": False, "message": str(exc)}), 400
    return jsonify(result), 200


@automation_bp.get("/validate/phone/<string:phone>")
@require_auth
def validate_phone(phone: str):
    """Valida telefone angolano (9 dígitos, começa por 9) via Angola API."""
    container: Container = automation_bp.container  # type: ignore[attr-defined]
    optional = request.args.get("optional", "false").lower() == "true"
    try:
        result = container.validate_angola_phone_use_case.execute(phone, optional=optional)
    except ValidationError as exc:
        return jsonify({"valid": False, "message": str(exc)}), 400
    return jsonify(result), 200


@automation_bp.get("/banks/<string:bank_code>/branches")
@require_auth
def list_bank_branches(bank_code: str):
    """Lista agências activas do banco (opcionalmente filtradas por província)."""
    container: Container = automation_bp.container  # type: ignore[attr-defined]
    province = request.args.get("province")
    try:
        result = container.list_bank_branches_use_case.execute(bank_code, province=province)
    except ValidationError as exc:
        return jsonify({"error": {"code": "validation_error", "message": str(exc)}}), 400
    return jsonify(result), 200


@automation_bp.get("/banks/<string:bank_code>/discount-rate")
@require_auth
def get_bank_discount_rate(bank_code: str):
    """Obtém taxa de juro/desconto real por scraping do site do banco."""
    container: Container = automation_bp.container  # type: ignore[attr-defined]
    sector = request.args.get("sector")
    result = container.get_bank_discount_rate_use_case.execute(
        bank_code, sector=sector
    )
    return jsonify(result), 200
