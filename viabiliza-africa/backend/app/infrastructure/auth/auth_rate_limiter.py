"""Rate limiting simples em memória para endpoints de autenticação."""

from __future__ import annotations

import threading
import time
from collections import defaultdict

from app.domain.exceptions.domain_exceptions import ValidationError


class AuthRateLimiter:
    def __init__(self, *, max_attempts: int = 12, window_seconds: int = 900) -> None:
        self._max = max_attempts
        self._window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def _key(self, scope: str, identifier: str) -> str:
        return f"{scope}:{identifier.strip().lower()}"

    def check(self, scope: str, identifier: str) -> None:
        if not identifier:
            return
        now = time.time()
        key = self._key(scope, identifier)
        with self._lock:
            window_start = now - self._window
            self._hits[key] = [t for t in self._hits[key] if t >= window_start]
            if len(self._hits[key]) >= self._max:
                raise ValidationError(
                    "Demasiadas tentativas. Aguarde alguns minutos e tente novamente."
                )
            self._hits[key].append(now)
