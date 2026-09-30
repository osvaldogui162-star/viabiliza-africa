"""Probe Angolan bank sites for rates and logo URLs."""
from __future__ import annotations

import os
import re
from urllib.parse import urljoin

import requests

H = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-PT,pt;q=0.9",
}

BANKS = {
    "bfa": "https://www.bfa.ao/",
    "bda": "https://www.bda.ao/",
    "bic": "https://www.bancobic.ao/",
    "atl": "https://www.atlantico.ao/",
    "bai": "https://www.bancobai.ao/",
    "sba": "https://www.standardbank.co.ao/",
    "bpc": "https://www.bpc.ao/",
    "keve": "https://www.bancokeve.ao/",
    "sol": "https://www.bancosol.ao/",
    "bni": "https://www.bni.ao/",
    "bcga": "https://www.caixaangola.ao/",
    "bci": "https://www.bci.ao/",
    "economico": "https://www.bancoeconomico.ao/",
}

OUT = os.path.join(
    os.path.dirname(__file__), "..", "..", "frontend", "public", "banks"
)
os.makedirs(OUT, exist_ok=True)


def main() -> None:
    for code, url in BANKS.items():
        try:
            r = requests.get(url, headers=H, timeout=25, allow_redirects=True)
            print(f"\n== {code} {r.status_code} {r.url} len={len(r.text)}")
            html = r.text
            rates = re.findall(
                r"(?is)taxa[^%]{0,60}?(\d{1,2}(?:[.,]\d{1,2})?)\s*%", html
            )
            print(" rates sample:", rates[:10])
            logos: set[str] = set()
            for m in re.finditer(
                r'(?:og:image|twitter:image)["\'\s]+content=["\']([^"\']+)',
                html,
                re.I,
            ):
                logos.add(urljoin(r.url, m.group(1)))
            for m in re.finditer(
                r'src=["\']([^"\']*logo[^"\']*\.(?:png|jpg|jpeg|svg|webp)[^"\']*)',
                html,
                re.I,
            ):
                logos.add(urljoin(r.url, m.group(1)))
            for m in re.finditer(
                r'<link[^>]+rel=["\'][^"\']*icon[^"\']*["\'][^>]+href=["\']([^"\']+)',
                html,
                re.I,
            ):
                logos.add(urljoin(r.url, m.group(1)))
            print(" logos:", list(logos)[:10])
            credits = re.findall(
                r'href=["\']([^"\']*(?:credito|crédito|financi|precario|preçário)[^"\']*)',
                html,
                re.I,
            )
            print(" credit links:", credits[:8])
        except Exception as e:
            print(f"\n== {code} ERROR {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
