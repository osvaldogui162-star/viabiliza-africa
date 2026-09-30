"""Download official bank logos into frontend/public/banks."""
from __future__ import annotations

import os
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

H = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
}

# Prefer SVG / PNG brand marks from each bank's portal
LOGO_CANDIDATES: dict[str, list[str]] = {
    "bfa": [
        "https://www.bfa.ao/images/logos/logo-mobile.svg",
        "https://www.bfa.ao/images/favicons/apple-touch-icon.png",
    ],
    "bda": [
        "https://www.bda.ao/theme/images/bda-logo.svg",
        "https://www.bda.ao/media/2023/06/bda-logo.png",
    ],
    "bic": [
        "https://www.bancobic.ao/application/images/logos/logo-gray.svg",
        "https://www.bic.ao/application/images/logos/logo-gray.svg",
    ],
    "atl": [
        "https://www.atlantico.ao/media/h10df34n/0-logo-atlanticosvg.png",
        "https://www.atlantico.ao/media/e2ziawnf/smalllogo.png",
    ],
    "bai": [
        "https://www.bancobai.ao/media/2684/logo-bai.svg",
        "https://www.bancobai.ao/media/2584/logo-bai.svg",
    ],
    "sba": [
        "https://www.standardbank.co.ao/static_file/assets/favicons/android-icon-192x192.png",
        "https://www.standardbank.co.ao/static_file/assets/favicons/apple-icon-180x180.png",
    ],
    "bpc": [
        "https://res.cloudinary.com/dq09gxdoc/image/upload/v1740045556/Logos_BPC_BPC_Cor_comercial_branco_vertical_-_C%C3%B3pia-removebg-preview_c7ywpq.png",
        "https://www.bpc.ao/favicon.ico",
    ],
    "keve": [
        "https://www.bancokeve.ao/Content/images/logo.png",
        "https://bancokeve.ao/Content/images/logo.png",
        "https://www.bancokeve.ao/favicon.ico",
    ],
    "sol": [
        "https://www.bancosol.ao/hubfs/Vector.png",
    ],
    "bni": [
        "https://www.bni.ao/Content/Images/logo_rsp.svg",
        "https://www.bni.ao/Content/Images/logo_header.png?v=1",
        "https://www.bni.ao/Content/Images/logo.png",
    ],
    "bcga": [
        "https://www.caixaangola.ao/Content/Images/logo.png",
        "https://www.caixaangola.ao/favicon.ico",
        "https://logo.clearbit.com/caixaangola.ao",
    ],
    "bci": [
        "https://www.bci.ao/assets/images/logos/favicon.svg",
        "https://www.bci.ao/assets/images/logos/logo.svg",
        "https://logo.clearbit.com/bci.ao",
    ],
    "economico": [
        "https://www.bancoeconomico.ao/media/1182/logo-particulares-white.svg",
        "https://www.bancoeconomico.ao/Assets/images/favico/favicon-196x196.png",
    ],
}

OUT = Path(__file__).resolve().parents[2] / "frontend" / "public" / "banks"
OUT.mkdir(parents=True, exist_ok=True)


def _ext_from(url: str, content_type: str) -> str:
    lower = url.lower().split("?")[0]
    for ext in (".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico"):
        if lower.endswith(ext):
            return ext
    if "svg" in content_type:
        return ".svg"
    if "jpeg" in content_type or "jpg" in content_type:
        return ".jpg"
    if "webp" in content_type:
        return ".webp"
    if "icon" in content_type:
        return ".ico"
    return ".png"


def download_one(code: str, urls: list[str]) -> Path | None:
    for url in urls:
        try:
            r = requests.get(url, headers=H, timeout=30, verify=False, allow_redirects=True)
            if r.status_code != 200 or len(r.content) < 200:
                print(f"  skip {url} status={r.status_code} size={len(r.content)}")
                continue
            ct = r.headers.get("content-type", "")
            if "html" in ct and "svg" not in ct:
                print(f"  skip html {url}")
                continue
            ext = _ext_from(url, ct)
            path = OUT / f"{code}{ext}"
            # remove previous variants
            for old in OUT.glob(f"{code}.*"):
                old.unlink()
            path.write_bytes(r.content)
            print(f"OK {code} <- {url} ({len(r.content)} bytes -> {path.name})")
            return path
        except Exception as exc:
            print(f"  fail {url}: {exc}")
    print(f"FAIL {code}: no logo downloaded")
    return None


def main() -> None:
    for code, urls in LOGO_CANDIDATES.items():
        download_one(code, urls)


if __name__ == "__main__":
    main()
