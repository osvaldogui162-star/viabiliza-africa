"""Convert/fix remaining bank logos."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

OUT = Path(__file__).resolve().parents[2] / "frontend" / "public" / "banks"

# Minimal official-style marks when portals block hotlinking (BPC / Caixa Angola).
# Colors match public brand identities of each bank.
BPC_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 80" role="img" aria-label="BPC">
  <rect width="240" height="80" rx="8" fill="#0B3D91"/>
  <text x="120" y="52" text-anchor="middle" font-family="Arial Black, Arial, sans-serif" font-size="36" fill="#FFFFFF" font-weight="700">BPC</text>
</svg>
"""

BCGA_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 80" role="img" aria-label="Caixa Angola">
  <rect width="280" height="80" rx="8" fill="#C8102E"/>
  <text x="140" y="36" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#FFFFFF" font-weight="600">CAIXA</text>
  <text x="140" y="60" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#FFFFFF" font-weight="700">ANGOLA</text>
</svg>
"""

SOL_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 80" role="img" aria-label="Banco Sol">
  <rect width="240" height="80" rx="8" fill="#F5A623"/>
  <circle cx="46" cy="40" r="18" fill="#FFFFFF"/>
  <text x="150" y="48" text-anchor="middle" font-family="Arial Black, Arial, sans-serif" font-size="28" fill="#1A1A1A" font-weight="700">SOL</text>
</svg>
"""


def main() -> None:
    ico = OUT / "bpc.ico"
    if ico.exists():
        try:
            im = Image.open(ico).convert("RGBA")
            im.save(OUT / "bpc.png")
            print("converted bpc.ico -> bpc.png", im.size)
        except Exception as exc:
            print("ico convert failed", exc)
            (OUT / "bpc.svg").write_text(BPC_SVG, encoding="utf-8")
            print("wrote bpc.svg fallback")
    else:
        (OUT / "bpc.svg").write_text(BPC_SVG, encoding="utf-8")
        print("wrote bpc.svg")

    if not (OUT / "bcga.png").exists() and not (OUT / "bcga.svg").exists():
        (OUT / "bcga.svg").write_text(BCGA_SVG, encoding="utf-8")
        print("wrote bcga.svg")

    # Prefer a larger Sol mark if current png is tiny
    sol = OUT / "sol.png"
    if sol.exists() and sol.stat().st_size < 1500:
        (OUT / "sol.svg").write_text(SOL_SVG, encoding="utf-8")
        sol.unlink(missing_ok=True)
        print("replaced tiny sol.png with sol.svg")


if __name__ == "__main__":
    main()
