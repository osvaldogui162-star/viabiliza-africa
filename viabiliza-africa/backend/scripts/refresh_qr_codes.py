"""Regenera QR Codes de orçamentos/proformas com o FRONTEND_BASE_URL actual."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from app.config import Config, detect_lan_ip  # noqa: E402
from app.infrastructure.qrcode.qr_code_service import QRCodeService  # noqa: E402
from app.infrastructure.supabase.client import create_supabase_client  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerar imagens mesmo quando o URL já está correcto",
    )
    args = parser.parse_args()

    config = Config()
    print(f"LAN_IP={detect_lan_ip()}")
    print(f"FRONTEND_BASE_URL={config.FRONTEND_BASE_URL}")

    client = create_supabase_client(config)
    qr = QRCodeService()
    base = config.FRONTEND_BASE_URL.rstrip("/")

    budgets = client.table("budgets").select("id,verification_hash,qr_code_data").execute().data or []
    updated_budgets = 0
    for row in budgets:
        h = row.get("verification_hash")
        if not h:
            continue
        verify_url = f"{base}/verify/budget/{h}"
        if not args.force and row.get("qr_code_data") == verify_url and row.get("qr_code_image"):
            continue
        image = qr.generate(verify_url)
        client.table("budgets").update(
            {"qr_code_data": image.data, "qr_code_image": image.image_base64}
        ).eq("id", row["id"]).execute()
        updated_budgets += 1
        print(f"BUDGET {row['id'][:8]}... -> {verify_url}")

    proformas = (
        client.table("proforma_invoices")
        .select("id,budget_id,qr_code_data")
        .execute()
        .data
        or []
    )
    # Map budget_id → hash
    hash_by_budget = {
        row["id"]: row.get("verification_hash")
        for row in budgets
        if row.get("verification_hash")
    }
    updated_proformas = 0
    for row in proformas:
        h = hash_by_budget.get(row.get("budget_id"))
        if not h:
            continue
        verify_url = f"{base}/verify/budget/{h}"
        if not args.force and row.get("qr_code_data") == verify_url:
            continue
        image = qr.generate(verify_url)
        client.table("proforma_invoices").update(
            {"qr_code_data": image.data, "qr_code_image": image.image_base64}
        ).eq("id", row["id"]).execute()
        updated_proformas += 1
        print(f"PROFORMA {row['id'][:8]}... -> {verify_url}")

    print(f"UPDATED_BUDGETS={updated_budgets}")
    print(f"UPDATED_PROFORMAS={updated_proformas}")
    print("DONE")
    print(f"TEST_URL={base}/verify/budget/0787719ccedc3ced9a6373154a21de2b6b93ef28823e731c246a9b349bf5e317")


if __name__ == "__main__":
    main()
