"""Apply migration 017 against DATABASE_URL and verify columns."""
from __future__ import annotations

import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

EXPECTED = [
    "rep_full_name",
    "rep_email",
    "rep_id_number",
    "rep_phone",
    "rep_role",
    "company_province",
    "company_municipality",
    "company_address",
    "company_activity",
    "company_phone",
    "company_email",
    "company_website",
    "company_latitude",
    "company_longitude",
    "geocode_verified",
    "geocode_source",
    "financing_type",
    "loan_term_months",
    "bank_branch",
]


def main() -> None:
    load_dotenv()
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if not database_url:
        raise SystemExit("DATABASE_URL em falta")

    sql_path = Path(__file__).resolve().parents[1] / "migrations" / "supabase" / "017_project_extended_fields.sql"
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
                  AND table_name = 'projects'
                  AND column_name = ANY(%s)
                ORDER BY column_name
                """,
                (EXPECTED,),
            )
            cols = [row[0] for row in cur.fetchall()]
            # Force PostgREST to notice schema changes when possible (Supabase)
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
