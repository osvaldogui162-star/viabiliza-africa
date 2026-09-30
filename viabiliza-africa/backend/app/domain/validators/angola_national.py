"""Validadores nacionais angolanos (formato Angola API)."""

from __future__ import annotations

import re

# Fonte: Angola-Api/Angola-Api — validateBi.ts
BI_PATTERN = re.compile(r"^\d{9}[A-Za-z]{2}\d{3}$")

# Contacto móvel local: 9 dígitos, começa por 9
LOCAL_PHONE_PATTERN = re.compile(r"^9\d{8}$")

# Angola API validatePhone.ts (+244 + 9 dígitos)
INTERNATIONAL_PHONE_PATTERN = re.compile(r"^\+244\d{9}$")


def normalize_bi(value: str) -> str:
    return value.strip().upper().replace(" ", "")


def normalize_local_phone(value: str) -> str:
    digits = re.sub(r"\D", "", value.strip())
    if digits.startswith("244") and len(digits) >= 12:
        digits = digits[3:]
    if digits.startswith("0") and len(digits) == 10:
        digits = digits[1:]
    return digits[:9]


def to_international_phone(local_phone: str) -> str:
    normalized = normalize_local_phone(local_phone)
    return f"+244{normalized}"


def is_valid_bi_format(value: str) -> bool:
    return bool(BI_PATTERN.match(normalize_bi(value)))


def is_valid_local_phone(value: str) -> bool:
    return bool(LOCAL_PHONE_PATTERN.match(normalize_local_phone(value)))


def is_valid_international_phone(value: str) -> bool:
    return bool(INTERNATIONAL_PHONE_PATTERN.match(value.strip()))


def validate_bi_format(value: str) -> str:
    normalized = normalize_bi(value)
    if not normalized:
        raise ValueError("Número do BI é obrigatório")
    if not is_valid_bi_format(normalized):
        raise ValueError(
            "Formato de BI inválido. Use 9 dígitos + 2 letras + 3 dígitos (ex: 006151112LA041)"
        )
    return normalized


def validate_local_phone(value: str, *, field_label: str = "Contacto") -> str:
    normalized = normalize_local_phone(value)
    if not normalized:
        raise ValueError(f"{field_label} é obrigatório")
    if not is_valid_local_phone(normalized):
        raise ValueError(f"{field_label} inválido: 9 dígitos numéricos começando por 9")
    return normalized
