"""Apply migration 019 against DATABASE_URL and verify columns."""
from __future__ import annotations

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

EXPECTED = ["qr_code_data", "qr_code_image"]


def main() -> None:
    load_dotenv()
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if not database_url:
        raise SystemExit("DATABASE_URL em falta")

    sql_path = (
        Path(__file__).resolve().parents[1]
        / "migrations"
        / "supabase"
        / "019_proforma_qr_code.sql"
    )
    sql = sql_path.read_text(encoding="utf-8")

    conn = psycopg2.connect(database_url)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            cur.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'proforma_invoices'
                  AND column_name = ANY(%s)
                ORDER BY column_name
                """,
                (EXPECTED,),
            )
            cols = [row[0] for row in cur.fetchall()]
            try:
                cur.execute("NOTIFY pgrst, 'reload schema'")
            except Exception as exc:  # noqa: BLE001
                print(f"NOTIFY_SKIP: {exc}")
    finally:
        conn.close()

    missing = [name for name in EXPECTED if name not in cols]
    print("MIGRATION_OK")
    print(f"COLUMNS_FOUND={len(cols)}")
    print("FOUND=" + ",".join(cols))
    if missing:
        print("MISSING=" + ",".join(missing))
        raise SystemExit(1)
    print("ALL_COLUMNS_PRESENT")


if __name__ == "__main__":
    main()
