"""Recursos visuais da marca para emails transaccionais."""

from __future__ import annotations

import base64
from functools import lru_cache
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
PROJECT_ROOT = Path(__file__).resolve().parents[4]

BRAND_NAME = "ViabilizA+ África"
BRAND_TAGLINE = "Inteligência de investimento para o continente africano."

# Paleta oficial (auth / UI)
COLOR_NAVY = "#011636"
COLOR_TEAL = "#00777f"
COLOR_TEAL_LIGHT = "#008f96"
COLOR_AMBER = "#ffa900"
COLOR_TEXT = "#111827"
COLOR_MUTED = "#6b7280"
COLOR_BORDER = "#e5e7eb"
COLOR_SURFACE = "#ffffff"

_LOGO_CANDIDATES = (
    ASSETS_DIR / "viabiliza-africa-logo-light.png",
    PROJECT_ROOT / "frontend" / "public" / "brand" / "viabiliza-africa-logo-light.png",
)


@lru_cache(maxsize=1)
def get_brand_logo_data_uri() -> str | None:
    for path in _LOGO_CANDIDATES:
        if path.is_file():
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"data:image/png;base64,{encoded}"
    return None
