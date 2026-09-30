"""Probe AGT NIF with full form POST."""
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
    session = requests.Session()
    session.headers.update(HEADERS)
    page = session.get(URL, timeout=25)
    page.raise_for_status()
    html = page.text
    views = re.findall(
        r'id="([^"]*javax\.faces\.ViewState[^"]*)"[^>]*value="([^"]+)"',
        html,
    )
    print("views", views)
    viewstate = views[-1][1] if views else None
    if not viewstate:
        m = re.search(r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', html)
        viewstate = m.group(1) if m else None
    print("viewstate", viewstate[:40] if viewstate else None)

    # Try classic post
    payload = {
        "j_id_1u": "j_id_1u",
        "j_id_1u:txtNIFNumber": nif,
        "j_id_1u:j_id_21": "Pesquisar",
        "javax.faces.ViewState": viewstate,
        "j_id_1u_SUBMIT": "1",
    }
    resp = session.post(URL, data=payload, headers={"Referer": URL}, timeout=30)
    print("full post", resp.status_code, len(resp.text))
    for key in ["Nome", "Contribuinte", "Morada", "Actividade", "problema", "encontrado", "erro"]:
        if key.lower() in resp.text.lower():
            print("has", key)
    # print panel content
    m = re.search(
        r'id="showpanelNIF_content"[^>]*>(.*?)</div>\s*</div>\s*<script id="showpanelNIF',
        resp.text,
        re.S | re.I,
    )
    if m:
        print("PANEL", m.group(1)[:1500])
    else:
        # growl messages
        for gm in re.findall(r"detail:\"([^\"]+)\"", resp.text):
            print("MSG", gm)
        print(resp.text[resp.text.lower().find("showpanelnif") : resp.text.lower().find("showpanelnif") + 800])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "5000978702")
