"""
Aplica migrations SQL ao Supabase via conexão PostgreSQL directa.

Requer DATABASE_URL no .env (Supabase → Settings → Database → Connection string).

Uso:
    python -m scripts.apply_migrations
    python -m scripts.apply_migrations --file migrations/supabase/002_module2_projects.sql
"""
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(override=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Aplicar migrations SQL")
    parser.add_argument(
        "--file",
        default=None,
        help="Ficheiro SQL específico (por defeito aplica todos em migrations/supabase/)",
    )
    args = parser.parse_args()

    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        print(
            "Erro: DATABASE_URL não definido no .env\n"
            "Obtenha em Supabase → Settings → Database → Connection string (URI)\n"
            "Alternativa: execute o SQL manualmente no SQL Editor do Supabase.",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        import psycopg2
    except ImportError:
        print("Instale psycopg2: pip install psycopg2-binary", file=sys.stderr)
        sys.exit(1)

    migrations_dir = Path(__file__).resolve().parent.parent / "migrations" / "supabase"
    if args.file:
        files = [Path(args.file)]
    else:
        files = sorted(migrations_dir.glob("*.sql"))

    if not files:
        print("Nenhuma migration encontrada.", file=sys.stderr)
        sys.exit(1)

    conn = psycopg2.connect(database_url)
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            for sql_file in files:
                print(f"A aplicar: {sql_file.name}")
                sql = sql_file.read_text(encoding="utf-8")
                cur.execute(sql)
                print(f"  ✓ {sql_file.name}")
    finally:
        conn.close()

    print("Migrations aplicadas com sucesso.")


if __name__ == "__main__":
    main()
