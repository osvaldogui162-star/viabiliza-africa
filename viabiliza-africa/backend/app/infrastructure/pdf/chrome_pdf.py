"""Conversão HTML → PDF via Chrome/Edge headless (alta fidelidade ao modelo)."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path


def _browser_candidates() -> list[Path]:
    env = os.environ.get("VIABILIZA_CHROME_PATH") or os.environ.get("CHROME_PATH")
    candidates: list[Path] = []
    if env:
        candidates.append(Path(env))
    candidates.extend(
        [
            Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
            Path("/usr/bin/google-chrome"),
            Path("/usr/bin/google-chrome-stable"),
            Path("/usr/bin/chromium"),
            Path("/usr/bin/chromium-browser"),
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
        ]
    )
    return [p for p in candidates if p.is_file()]


def html_to_pdf(html: str, *, timeout_sec: int = 90) -> bytes:
    """Imprime HTML completo para PDF (A4) com Chrome/Edge headless."""
    browsers = _browser_candidates()
    if not browsers:
        raise RuntimeError(
            "Chrome/Edge não encontrado. Defina VIABILIZA_CHROME_PATH ou instale o browser."
        )

    with tempfile.TemporaryDirectory(prefix="viabiliza_report_") as tmp:
        tmp_path = Path(tmp)
        html_path = tmp_path / "report.html"
        pdf_path = tmp_path / "report.pdf"
        html_path.write_text(html, encoding="utf-8")

        # file:/// URL (Windows: file:///C:/...)
        uri = html_path.resolve().as_uri()
        args = [
            str(browsers[0]),
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--no-first-run",
            "--disable-extensions",
            f"--print-to-pdf={pdf_path}",
            "--print-to-pdf-no-header",
            uri,
        ]
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        if not pdf_path.is_file() or pdf_path.stat().st_size < 500:
            raise RuntimeError(
                "Falha ao gerar PDF via browser: "
                f"code={result.returncode} stderr={(result.stderr or '')[:400]}"
            )
        return pdf_path.read_bytes()
