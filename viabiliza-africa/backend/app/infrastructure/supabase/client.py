from functools import lru_cache

import httpx
from gotrue import SyncMemoryStorage
from supabase import Client, ClientOptions, create_client

from app.config import Config


def _configure_http1_session(client: Client) -> Client:
    """Força HTTP/1.1 no PostgREST para evitar ConnectionTerminated em HTTP/2."""
    postgrest = client.postgrest
    old_session = postgrest.session
    postgrest.session = httpx.Client(
        base_url=str(old_session.base_url),
        headers=dict(old_session.headers),
        timeout=old_session.timeout,
        follow_redirects=True,
        http2=False,
    )
    old_session.close()
    return client


@lru_cache(maxsize=1)
def get_supabase_client(url: str, key: str) -> Client:
    options = ClientOptions(
        storage=SyncMemoryStorage(),
        persist_session=False,
        auto_refresh_token=False,
    )
    client = create_client(url, key, options)
    return _configure_http1_session(client)


def create_supabase_client(config: Config) -> Client:
    config.validate()
    return get_supabase_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_ROLE_KEY)
