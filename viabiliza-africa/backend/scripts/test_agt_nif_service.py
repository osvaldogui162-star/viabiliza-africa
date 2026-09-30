"""Smoke test AgtNifLookupService against live portal."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.infrastructure.scraping.agt_nif_lookup import AgtNifLookupService


def main() -> None:
    service = AgtNifLookupService()
    for nif in sys.argv[1:] or ["5410003284", "5410003144", "9999999999"]:
        try:
            result = service.lookup(nif)
            print("OK", nif, "->", result.company_name)
            print("  status:", result.status)
            print("  fields:", result.raw_fields)
            print("  source:", result.source_url)
        except Exception as exc:
            print("ERR", nif, "->", type(exc).__name__, exc)


if __name__ == "__main__":
    main()
