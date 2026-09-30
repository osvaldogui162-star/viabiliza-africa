"""Probe Portal do Contribuinte NIF page."""
from __future__ import annotations

import re
import sys

import requests

URL = "https://portaldocontribuinte.minfin.gov.ao/consultar-nif-do-contribuinte"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
}


def main(nif: str) -> None:
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session = requests.Session()
    session.headers.update(HEADERS)
    session.verify = False
    page = session.get(URL, timeout=30, allow_redirects=True)
    print("GET", page.status_code, page.url, len(page.text))
    html = page.text
    out = "scripts/_portal_nif_page.html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print("saved", out)

    for m in re.finditer(r"<form[^>]*>", html, re.I):
        print("FORM", m.group(0)[:400])

    for pat in ["txtNIF", "NIFNumber", "ViewState", "showpanel", "Pesquisar", "j_id"]:
        print(f"count {pat}:", len(re.findall(pat, html, re.I)))

    names = re.findall(r'name="([^"]+)"', html)
    interesting = [
        n
        for n in names
        if any(x in n.lower() for x in ("nif", "view", "submit", "j_id", "pesquis"))
    ]
    print("interesting names:", interesting)

    # dump form region around NIF
    idx = html.lower().find("nif")
    if idx >= 0:
        print("--- region ---")
        print(html[max(0, idx - 400) : idx + 1200])

    viewstate = None
    m = re.search(r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', html)
    if m:
        viewstate = m.group(1)
    print("viewstate", (viewstate[:50] + "...") if viewstate else None)

    # Discover form id / button from HTML
    form_ids = re.findall(r'id="(j_id_[^"]+)"[^>]*name="(j_id_[^"]+)"', html)
    print("form ids", form_ids[:20])
    nif_inputs = re.findall(
        r'id="([^"]*NIF[^"]*)"[^>]*name="([^"]*)"|name="([^"]*NIF[^"]*)"',
        html,
        re.I,
    )
    print("nif inputs", nif_inputs)

    buttons = re.findall(
        r'<(?:button|input)[^>]*(?:value|id|name)="[^"]*[Pp]esquis[^"]*"[^>]*>',
        html,
    )
    print("buttons", buttons[:10])
    for b in re.finditer(
        r'<input[^>]*type="submit"[^>]*>|<button[^>]*>[^<]*[Pp]esquis',
        html,
    ):
        print("BTN", b.group(0)[:300])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "5000978702")
