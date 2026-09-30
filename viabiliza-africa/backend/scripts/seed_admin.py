"""
Cria o primeiro administrador da plataforma.

Uso:
    python -m scripts.seed_admin --email admin@viabiliza.africa --password "SenhaSegura123" --name "Administrador"
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(override=True)

from app.config import Config
from app.di.container import build_container
from app.domain.enums.user_role import UserRole
from app.domain.exceptions.domain_exceptions import ConflictError, DomainException


def _format_error(exc: Exception) -> str:
    message = getattr(exc, "message", str(exc))
    details = getattr(exc, "details", None) or getattr(exc, "args", None)
    if details and str(details) not in message:
        return f"{message} | Detalhes: {details}"
    return message


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed do administrador inicial")
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--name", default="Administrador")
    args = parser.parse_args()

    config = Config()
    try:
        config.validate()
    except ValueError as exc:
        print(f"Erro de configuração: {exc}", file=sys.stderr)
        print("Verifique SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY no ficheiro .env", file=sys.stderr)
        sys.exit(1)

    try:
        container = build_container(config)
    except Exception as exc:
        print(f"Erro ao ligar ao Supabase: {_format_error(exc)}", file=sys.stderr)
        sys.exit(1)

    try:
        existing = container.user_repository.find_by_email(args.email.lower())
    except Exception as exc:
        print(f"Erro ao consultar utilizadores: {_format_error(exc)}", file=sys.stderr)
        print(
            "Confirme que executou migrations/supabase/001_module1_auth.sql no Supabase.",
            file=sys.stderr,
        )
        sys.exit(1)

    if existing:
        if existing.role == UserRole.ADMIN:
            print(f"Administrador já existe: {args.email}")
            return
        container.user_repository.update(
            existing.id,
            role=UserRole.ADMIN,
            password_hash=container.password_hasher.hash(args.password),
        )
        print(f"Utilizador existente promovido a admin: {args.email}")
        return

    password_hash = container.password_hasher.hash(args.password)
    user = container.user_repository.create(
        email=args.email.lower(),
        full_name=args.name,
        password_hash=password_hash,
        role=UserRole.ADMIN,
    )
    print(f"Administrador criado: {user.email} (id={user.id})")


if __name__ == "__main__":
    try:
        main()
    except (ConflictError, DomainException) as exc:
        print(f"Erro: {exc.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Erro inesperado: {_format_error(exc)}", file=sys.stderr)
        sys.exit(1)
