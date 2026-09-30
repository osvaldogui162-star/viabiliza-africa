"""Utilitários para normalizar respostas do cliente Supabase/PostgREST."""


def get_rows(response) -> list[dict]:
    """Extrai lista de registos de uma resposta Supabase."""
    if response is None:
        return []
    data = getattr(response, "data", None)
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    return []


def get_single_row(response) -> dict | None:
    """Extrai um único registo ou None se não existir."""
    rows = get_rows(response)
    return rows[0] if rows else None
