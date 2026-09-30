"""Extracção básica de dados de empresa a partir de PDF/DOCX."""

from __future__ import annotations

import re
from io import BytesIO


_NIF_RE = re.compile(r"\b(?:NIF|N\.?I\.?F\.?|Contribuinte)\s*[:\-]?\s*(\d{9,14})\b", re.I)
_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
_PHONE_RE = re.compile(r"(?:\+244\s?)?9\d{2}[\s\-]?\d{3}[\s\-]?\d{3}")
_COMPANY_HINT_RE = re.compile(
    r"(?:Denomina(?:ção|cao)|Raz[aã]o\s+Social|Empresa|Firma)\s*[:\-]\s*(.+)",
    re.I,
)


class CompanyDocumentExtractor:
    def extract(self, file_bytes: bytes, *, filename: str) -> dict:
        text = self._read_text(file_bytes, filename)
        cleaned = " ".join(text.split())
        nif = self._find_nif(cleaned)
        return {
            "nif": nif,
            "company_name": self._find_company_name(text),
            "email": self._find_first(_EMAIL_RE, text),
            "phone": self._find_first(_PHONE_RE, text),
            "address": self._find_address(text),
            "activity": self._find_activity(text),
            "text_preview": cleaned[:1500],
            "fields_found": sum(
                1
                for value in (
                    nif,
                    self._find_company_name(text),
                    self._find_first(_EMAIL_RE, text),
                    self._find_first(_PHONE_RE, text),
                )
                if value
            ),
        }

    def _read_text(self, file_bytes: bytes, filename: str) -> str:
        lower = filename.lower()
        if lower.endswith(".pdf"):
            return self._read_pdf(file_bytes)
        if lower.endswith((".txt", ".csv")):
            return file_bytes.decode("utf-8", errors="ignore")
        raise ValueError("Formato não suportado. Use PDF ou TXT.")

    @staticmethod
    def _read_pdf(file_bytes: bytes) -> str:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise ValueError("Dependência pypdf necessária para ler PDF") from exc

        reader = PdfReader(BytesIO(file_bytes))
        pages = []
        for page in reader.pages[:20]:
            pages.append(page.extract_text() or "")
        return "\n".join(pages)

    @staticmethod
    def _find_nif(text: str) -> str | None:
        match = _NIF_RE.search(text)
        if match:
            return match.group(1).strip()
        fallback = re.search(r"\b(\d{9,10})\b", text)
        return fallback.group(1) if fallback else None

    @staticmethod
    def _find_company_name(text: str) -> str | None:
        match = _COMPANY_HINT_RE.search(text)
        if match:
            name = match.group(1).strip().split("\n")[0].strip(" .,-")
            if len(name) >= 3:
                return name[:200]
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line in lines[:8]:
            if len(line) >= 5 and not line.isdigit():
                return line[:200]
        return None

    @staticmethod
    def _find_first(pattern: re.Pattern[str], text: str) -> str | None:
        match = pattern.search(text)
        return match.group(0).strip() if match else None

    @staticmethod
    def _find_address(text: str) -> str | None:
        match = re.search(
            r"(?:Morada|Endere(?:ço|co)|Sede)\s*[:\-]\s*(.+)",
            text,
            re.I,
        )
        if match:
            return match.group(1).strip().split("\n")[0][:300]
        return None

    @staticmethod
    def _find_activity(text: str) -> str | None:
        match = re.search(
            r"(?:Actividade|Atividade|Objecto\s+Social)\s*[:\-]\s*(.+)",
            text,
            re.I,
        )
        if match:
            return match.group(1).strip().split("\n")[0][:300]
        return None
