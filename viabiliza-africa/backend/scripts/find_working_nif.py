"""Find a working Angolan NIF and dump successful panel HTML."""
from __future__ import annotations

import re
import sys

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://portaldocontribuinte.minfin.gov.ao"
URL = f"{BASE}/consultar-nif-do-contribuinte"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
}

# Known / public Angolan company NIFs to try
CANDIDATES = [
    "5410000866",  # Unitel (possible)
    "5000001022",
    "5000022102",
    "5000978702",
    "5401001234",
    "5000387872",
    "5403012345",
    "5001122334",
    "2417200679",
    "5000000866",
    "5400000001",
    "5000157200",
]


def discover_form(html: str) -> dict:
    nif_input = re.search(
        r'name="([^"]*txtNIFNumber)"',
        html,
        re.I,
    )
    if not nif_input:
        raise RuntimeError("Campo NIF não encontrado")
    nif_name = nif_input.group(1)
    form_prefix = nif_name.split(":")[0]

    form_action = re.search(
        rf'<form[^>]*id="{re.escape(form_prefix)}"[^>]*action="([^"]+)"',
        html,
        re.I,
    )
    action = form_action.group(1) if form_action else "/consultar-nif-do-contribuinte"
    if action.startswith("/"):
        action = BASE + action

    btn = re.search(
        rf'id="({re.escape(form_prefix)}:j_id_[^"]+)"[^>]*onclick="PrimeFaces\.ab\(\{{s:&quot;\1&quot;,p:&quot;{re.escape(form_prefix)}&quot;,u:&quot;([^&]+)&quot;',
        html,
    )
    if not btn:
        btn = re.search(
            rf'name="({re.escape(form_prefix)}:j_id_[^"]+)"[^>]*onclick="[^"]*showpanelNIF',
            html,
        )
        button_name = btn.group(1) if btn else f"{form_prefix}:j_id_34"
        update = "showpanelNIF"
    else:
        button_name = btn.group(1)
        update = btn.group(2)

    viewstate = re.search(
        r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"',
        html,
    )
    return {
        "form_prefix": form_prefix,
        "nif_name": nif_name,
        "button_name": button_name,
        "update": update,
        "action": action,
        "viewstate": viewstate.group(1) if viewstate else None,
        "submit_name": f"{form_prefix}_SUBMIT",
    }


def lookup(session: requests.Session, nif: str, form: dict) -> str:
    payload = {
        form["form_prefix"]: form["form_prefix"],
        form["nif_name"]: nif,
        form["button_name"]: "Pesquisar",
        "javax.faces.ViewState": form["viewstate"],
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": form["button_name"],
        "javax.faces.partial.execute": form["form_prefix"],
        "javax.faces.partial.render": form["update"],
        form["submit_name"]: "1",
    }
    # Also include growl in render if present
    growl = re.search(rf'{re.escape(form["form_prefix"])}:j_id_\d+', form.get("_html", ""))
    resp = session.post(
        form["action"],
        data=payload,
        headers={
            **HEADERS,
            "Faces-Request": "partial/ajax",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": URL,
            "Origin": BASE,
            "Accept": "application/xml, text/xml, */*; q=0.01",
        },
        timeout=35,
    )
    return resp.text


def main() -> None:
    nifs = sys.argv[1:] or CANDIDATES
    session = requests.Session()
    session.headers.update(HEADERS)
    session.verify = False

    page = session.get(URL, timeout=30)
    form = discover_form(page.text)
    form["_html"] = page.text
    print("FORM", {k: v for k, v in form.items() if k != "_html"})

    for nif in nifs:
        # refresh viewstate each time
        page = session.get(URL, timeout=30)
        form = discover_form(page.text)
        body = lookup(session, nif, form)
        msgs = re.findall(r'detail\s*:\s*"([^"]+)"', body)
        has_panel_data = "table" in body.lower() or "Nome" in body
        print(f"NIF {nif}: msgs={msgs} panel_data={has_panel_data} len={len(body)}")
        if has_panel_data and not any("não encontrado" in m.lower() or "nao encontrado" in m.lower() for m in msgs):
            with open("scripts/_portal_success.xml", "w", encoding="utf-8") as f:
                f.write(body)
            print("SUCCESS saved scripts/_portal_success.xml")
            print(body[:3000])
            return
    print("No success among candidates")


if __name__ == "__main__":
    main()
