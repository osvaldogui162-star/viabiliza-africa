"""Probe Portal do Contribuinte NIF lookup with correct form IDs."""
from __future__ import annotations

import re
import sys

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://portaldocontribuinte.minfin.gov.ao"
URL = f"{BASE}/consultar-nif-do-contribuinte"
POST_URL = f"{BASE}/consultar-headNifId-do-contribuinte"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
}


def extract_viewstate(html: str) -> str | None:
    m = re.search(r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"', html)
    return m.group(1) if m else None


def main(nif: str) -> None:
    session = requests.Session()
    session.headers.update(HEADERS)
    session.verify = False

    page = session.get(URL, timeout=30, allow_redirects=True)
    print("GET", page.status_code, page.url)
    html = page.text
    viewstate = extract_viewstate(html)
    print("viewstate", (viewstate[:40] + "...") if viewstate else None)

    # Inspect form region
    start = html.find('id="j_id_2x"')
    end = html.find("showpanelNIF")
    region = html[start : end + 800] if start >= 0 else ""
    print("--- FORM REGION ---")
    print(region[:3000])

    # Discover button value
    btn = re.search(
        r'id="j_id_2x:j_id_34"[^>]*(?:value="([^"]*)")?',
        html,
    )
    print("button match", btn.group(0)[:400] if btn else None, "value", btn.group(1) if btn else None)

    # Partial AJAX post (PrimeFaces)
    ajax_payload = {
        "j_id_2x": "j_id_2x",
        "j_id_2x:txtNIFNumber": nif,
        "j_id_2x:j_id_34": "Pesquisar",
        "javax.faces.ViewState": viewstate,
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": "j_id_2x:j_id_34",
        "javax.faces.partial.execute": "j_id_2x",
        "javax.faces.partial.render": "showpanelNIF j_id_2x:j_id_36",
        "j_id_2x_SUBMIT": "1",
    }

    # Discover render targets from onclick/script
    for m in re.finditer(r"PrimeFaces\.ab\((\{[^}]+\})\)", html):
        print("PF.ab", m.group(1)[:400])

    for post_url in (URL, POST_URL):
        print("\n=== AJAX POST", post_url, "===")
        resp = session.post(
            post_url,
            data=ajax_payload,
            headers={
                **HEADERS,
                "Faces-Request": "partial/ajax",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer": URL,
                "Origin": BASE,
            },
            timeout=35,
        )
        print("status", resp.status_code, "len", len(resp.text), "ctype", resp.headers.get("content-type"))
        print(resp.text[:2000])
        with open(f"scripts/_portal_ajax_{'nif' if post_url==URL else 'head'}.xml", "w", encoding="utf-8") as f:
            f.write(resp.text)

    # Full form post
    full_payload = {
        "j_id_2x": "j_id_2x",
        "j_id_2x:txtNIFNumber": nif,
        "j_id_2x:j_id_34": "Pesquisar",
        "javax.faces.ViewState": viewstate,
        "j_id_2x_SUBMIT": "1",
    }
    for post_url in (URL, POST_URL):
        print("\n=== FULL POST", post_url, "===")
        resp = session.post(
            post_url,
            data=full_payload,
            headers={**HEADERS, "Referer": URL, "Origin": BASE},
            timeout=35,
        )
        print("status", resp.status_code, "len", len(resp.text))
        for key in ["Nome", "Contribuinte", "Morada", "Actividade", "encontrado", "erro", "NIF"]:
            if key.lower() in resp.text.lower():
                print("has", key)
        m = re.search(
            r'id="showpanelNIF_content"[^>]*>(.*?)</div>\s*</div>\s*<script id="showpanelNIF',
            resp.text,
            re.S | re.I,
        )
        if m:
            print("PANEL", m.group(1)[:2000])
        else:
            idx = resp.text.lower().find("showpanelnif")
            print("panel idx", idx)
            if idx >= 0:
                print(resp.text[idx : idx + 1500])
        for gm in re.findall(r'detail\s*:\s*"([^"]+)"', resp.text):
            print("MSG", gm)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "5000978702")
