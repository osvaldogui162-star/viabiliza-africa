from __future__ import annotations

import secrets

from app.application.interfaces.hash_service import IHashService


API_KEY_PREFIX = "vza_"


def generate_billing_api_key() -> str:
    return f"{API_KEY_PREFIX}{secrets.token_urlsafe(32)}"


def hash_billing_api_key(raw_key: str, hash_service: IHashService) -> str:
    return hash_service.hash_string(raw_key.strip())


def api_key_hint(raw_key: str) -> str:
    key = raw_key.strip()
    if len(key) <= 8:
        return key
    return f"…{key[-8:]}"


def is_billing_api_key(value: str) -> bool:
    return value.startswith(API_KEY_PREFIX) and len(value) > len(API_KEY_PREFIX) + 16
