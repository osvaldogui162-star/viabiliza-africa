"""Dump AGT form fields and try alternate posts."""
from __future__ import annotations

import re

import requests

URL = "https://portaldocontribuinte.minfin.gov.ao/consultar-nif-do-contribuinte"
H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "pt-PT,pt;q=0.9",
}

s = requests.Session()
s.headers.update(H)
html = s.get(URL, timeout=25).text
open("scripts/_agt_page.html", "w", encoding="utf-8").write(html)
print("saved page")

# all name= attributes in form j_id_1u region
region = html[html.find("j_id_1u") : html.find("showpanelNIF") + 500]
print(region[:2500])
for m in re.finditer(r'detail:"([^"]+)"', html):
    print("detail", m.group(1))
