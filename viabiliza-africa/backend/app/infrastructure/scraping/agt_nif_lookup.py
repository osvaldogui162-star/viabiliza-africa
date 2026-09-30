from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from html import unescape
from urllib.parse import urljoin

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

AGT_NIF_URL = (
    "https://portaldocontribuinte.minfin.gov.ao/consultar-nif-do-contribuinte"
)
AGT_ORIGIN = "https://portaldocontribuinte.minfin.gov.ao"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
}


@dataclass(frozen=True)
class CompanyLookupResult:
    nif: str
    company_name: str | None
    address: str | None
    activity: str | None
    status: str | None
    source_url: str
    raw_fields: dict[str, str]


@dataclass(frozen=True)
class _FormSpec:
    form_prefix: str
    nif_field: str
    button_field: str
    update_targets: str
    action_url: str
    viewstate: str
    submit_field: str


class AgtNifLookupService:
    """Consulta NIF no Portal do Contribuinte (AGT / MINFIN) — dados reais."""

    def lookup(self, nif: str) -> CompanyLookupResult:
        cleaned = re.sub(r"\s+", "", nif or "").upper()
        if not cleaned or len(cleaned) < 5:
            raise ValueError("NIF inválido. Indique o NIF angolano completo.")

        session = self._session()
        page = session.get(AGT_NIF_URL, timeout=25)
        page.raise_for_status()
        form = self._discover_form(page.text)
        if not form:
            raise RuntimeError(
                "Portal AGT indisponível (formulário NIF em falta). "
                f"Consulte manualmente: {AGT_NIF_URL}"
            )

        response = session.post(
            form.action_url,
            data=self._ajax_payload(form, cleaned),
            headers={
                **HEADERS,
                "Faces-Request": "partial/ajax",
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Referer": AGT_NIF_URL,
                "Origin": AGT_ORIGIN,
                "Accept": "application/xml, text/xml, */*; q=0.01",
            },
            timeout=35,
        )
        response.raise_for_status()
        return self._parse_response(cleaned, response.text)

    def _session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update(HEADERS)
        # Certificado do portal Minfin frequentemente incompleto na cadeia local.
        session.verify = False
        return session

    def _discover_form(self, html: str) -> _FormSpec | None:
        nif_match = re.search(r'name="([^"]*txtNIFNumber)"', html, flags=re.I)
        if not nif_match:
            return None
        nif_field = nif_match.group(1)
        form_prefix = nif_field.split(":", 1)[0]

        action_match = re.search(
            rf'<form[^>]*\bid="{re.escape(form_prefix)}"[^>]*\baction="([^"]*)"',
            html,
            flags=re.I,
        )
        action_path = (
            action_match.group(1)
            if action_match and action_match.group(1)
            else "/consultar-nif-do-contribuinte"
        )
        action_url = urljoin(AGT_ORIGIN + "/", action_path.lstrip("/"))

        # onclick: PrimeFaces.ab({s:"form:btn",p:"form",u:"showpanelNIF"})
        btn_full = re.search(
            rf'name="({re.escape(form_prefix)}:j_id_[^"]+)"[^>]*'
            r'onclick="PrimeFaces\.ab\(\{{[^}}]*u:&quot;([^&]+)&quot;',
            html,
            flags=re.I,
        )
        if btn_full:
            button_field = btn_full.group(1)
            update = btn_full.group(2)
        else:
            btn_simple = re.search(
                rf'name="({re.escape(form_prefix)}:j_id_[^"]+)"[^>]*'
                r'onclick="[^"]*showpanelNIF',
                html,
                flags=re.I,
            )
            if not btn_simple:
                return None
            button_field = btn_simple.group(1)
            update = "showpanelNIF"

        growl_match = re.search(
            rf'id="({re.escape(form_prefix)}:j_id_\w+)"[^>]*class="[^"]*ui-growl',
            html,
            flags=re.I,
        )
        update_targets = update
        if growl_match:
            update_targets = f"{update} {growl_match.group(1)}"

        viewstate = self._extract_viewstate(html)
        if not viewstate:
            return None

        return _FormSpec(
            form_prefix=form_prefix,
            nif_field=nif_field,
            button_field=button_field,
            update_targets=update_targets,
            action_url=action_url,
            viewstate=viewstate,
            submit_field=f"{form_prefix}_SUBMIT",
        )

    def _ajax_payload(self, form: _FormSpec, nif: str) -> dict[str, str]:
        return {
            form.form_prefix: form.form_prefix,
            form.nif_field: nif,
            form.button_field: "Pesquisar",
            "javax.faces.ViewState": form.viewstate,
            "javax.faces.partial.ajax": "true",
            "javax.faces.source": form.button_field,
            "javax.faces.partial.execute": form.form_prefix,
            "javax.faces.partial.render": form.update_targets,
            form.submit_field: "1",
        }

    def _extract_viewstate(self, html: str) -> str | None:
        matches = re.findall(
            r'name="javax\.faces\.ViewState"[^>]*value="([^"]+)"',
            html,
        )
        return matches[-1] if matches else None

    def _parse_response(self, nif: str, body: str) -> CompanyLookupResult:
        errors = re.findall(r'detail\s*:\s*"([^"]+)"', body)
        panel = self._extract_panel_html(body)
        fields = self._extract_labeled_fields(panel or body)

        company_name = (
            fields.get("nome")
            or fields.get("nome do contribuinte")
            or fields.get("contribuinte")
            or fields.get("designação")
            or fields.get("designacao")
        )

        if company_name:
            return CompanyLookupResult(
                nif=nif,
                company_name=company_name.strip(),
                address=(
                    fields.get("morada")
                    or fields.get("endereço")
                    or fields.get("endereco")
                ),
                activity=fields.get("actividade") or fields.get("atividade"),
                status=(
                    fields.get("estado")
                    or fields.get("situação")
                    or fields.get("situacao")
                ),
                source_url=AGT_NIF_URL,
                raw_fields=fields,
            )

        fallback = self._lookup_full_post(nif)
        if fallback.company_name:
            return fallback

        message = errors[0] if errors else (
            "NIF não encontrado ou portal AGT sem resposta útil."
        )
        message = (
            message.replace("nÃ£o", "não")
            .replace("NÃ£o", "Não")
            .replace("n�o", "não")
            .replace("N�o", "Não")
        )
        raise LookupError(f"{message} Verifique o NIF em {AGT_NIF_URL}")

    def _extract_panel_html(self, body: str) -> str:
        panel_match = re.search(
            r'id="showpanelNIF_content"[^>]*>(.*?)</div>',
            body,
            flags=re.I | re.S,
        )
        panel = panel_match.group(1) if panel_match else ""

        for block in re.findall(r"<!\[CDATA\[(.*?)\]\]>", body, flags=re.S):
            if "showpanelNIF" in block or "panelNIF" in block or "Nome" in block:
                if len(block) > len(panel):
                    panel = block
        return panel

    def _lookup_full_post(self, nif: str) -> CompanyLookupResult:
        session = self._session()
        page = session.get(AGT_NIF_URL, timeout=25)
        form = self._discover_form(page.text)
        if not form:
            return CompanyLookupResult(
                nif=nif,
                company_name=None,
                address=None,
                activity=None,
                status=None,
                source_url=AGT_NIF_URL,
                raw_fields={},
            )

        resp = session.post(
            form.action_url,
            data={
                form.form_prefix: form.form_prefix,
                form.nif_field: nif,
                form.button_field: "Pesquisar",
                "javax.faces.ViewState": form.viewstate,
                form.submit_field: "1",
            },
            headers={**HEADERS, "Referer": AGT_NIF_URL, "Origin": AGT_ORIGIN},
            timeout=35,
        )
        fields = self._extract_labeled_fields(resp.text)
        company_name = (
            fields.get("nome")
            or fields.get("nome do contribuinte")
            or fields.get("contribuinte")
        )
        return CompanyLookupResult(
            nif=nif,
            company_name=company_name.strip() if company_name else None,
            address=fields.get("morada"),
            activity=fields.get("actividade") or fields.get("atividade"),
            status=fields.get("estado"),
            source_url=AGT_NIF_URL,
            raw_fields=fields,
        )

    def _extract_labeled_fields(self, html: str) -> dict[str, str]:
        fields: dict[str, str] = {}
        patterns = [
            # Portal do Contribuinte: <label>Nome:</label><div><label>VALOR</label>
            (
                r"<label[^>]*>\s*([^<:]{2,60}?)\s*:?\s*</label>\s*"
                r"<div[^>]*>\s*<label[^>]*>\s*([^<]+?)\s*</label>"
            ),
            r"<t[hd][^>]*>\s*([^<:]{2,40})\s*:?\s*</t[hd]>\s*<t[hd][^>]*>\s*([^<]+)\s*</t[hd]>",
            r"<label[^>]*>\s*([^<:]{2,40})\s*:?\s*</label>\s*[^<]*<[^>]+>\s*([^<]+)",
            r"<dt[^>]*>\s*([^<:]{2,40})\s*:?\s*</dt>\s*<dd[^>]*>\s*([^<]+)",
        ]
        for pattern in patterns:
            for label, value in re.findall(pattern, html, flags=re.I | re.S):
                key = unescape(re.sub(r"\s+", " ", label)).strip().lower().rstrip(":")
                val = unescape(re.sub(r"\s+", " ", value)).strip()
                if not key or key.startswith("<!--") or not val:
                    continue
                if val.lower() in ("", "-", "n/a"):
                    continue
                fields.setdefault(key, val)
        return fields


def parse_percent(raw: str) -> Decimal | None:
    cleaned = re.sub(r"[^\d,.\-]", "", raw.strip())
    if not cleaned:
        return None
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    try:
        value = Decimal(cleaned)
        return value if Decimal("0") < value <= Decimal("100") else None
    except InvalidOperation:
        return None
