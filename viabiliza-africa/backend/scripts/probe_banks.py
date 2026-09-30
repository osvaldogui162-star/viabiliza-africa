"""Probe bank rate pages."""
from __future__ import annotations

import re

import requests

H = {"User-Agent": "Mozilla/5.0"}

urls = [
    "https://www.bfa.ao/pt/private-banking/financiamento/credito-colateral-bfa/",
    "https://www.bfa.ao/pt/empresas/credito/credito-de-campanha-agricola-bfa/",
    "https://www.bfa.ao/pt/o-bfa/precario/precario/",
    "https://www.bai.ao/",
    "https://www.bic.ao/",
    "https://www.bda.ao/",
]

for u in urls:
    try:
        r = requests.get(u, headers=H, timeout=20)
        text = r.text
        rates = re.findall(r"(?i)taxa[^.<]{0,40}?(\d{1,2}(?:[.,]\d{1,2})?)\s*%", text)
        print(u, r.status_code, "rates", rates[:8], "len", len(text))
        pdfs = re.findall(r'href="([^"]+\.pdf)"', text, re.I)
        for p in pdfs[:5]:
            print("  pdf", p)
    except Exception as e:
        print(u, type(e).__name__, e)
