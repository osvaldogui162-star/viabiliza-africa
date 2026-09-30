"""Instituições financiadoras elegíveis para portal e vínculo de projecto."""

from app.domain.enums.financing_bank import FinancingBank


def is_portal_bank_code(code: str) -> bool:
    return FinancingBank.is_valid(code.strip().lower())


def validate_portal_bank_code(code: str | None) -> str:
    normalized = (code or "").strip().lower()
    if not is_portal_bank_code(normalized):
        names = ", ".join(FinancingBank.values())
        raise ValueError(
            f"Código de instituição inválido. Bancos disponíveis: {names}"
        )
    return normalized


def portal_bank_catalog() -> list[dict]:
    return [
        {
            "code": bank.value,
            "label_pt": bank.label_pt,
            "label_en": bank.label_pt,
            "website": bank.website,
            "logo_path": bank.logo_path,
        }
        for bank in FinancingBank
    ]
