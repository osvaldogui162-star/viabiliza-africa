from typing import Any

import requests

from app.domain.exceptions.domain_exceptions import ValidationError


class TrelloClient:
    """Cliente HTTP para a API REST do Trello."""

    BASE_URL = "https://api.trello.com/1"

    def __init__(self, api_key: str, api_token: str) -> None:
        if not api_key or not api_token:
            raise ValidationError(
                "TRELLO_API_KEY e TRELLO_API_TOKEN são obrigatórios para integração Trello"
            )
        self._api_key = api_key
        self._api_token = api_token

    def _auth_params(self) -> dict[str, str]:
        return {"key": self._api_key, "token": self._api_token}

    def post(self, path: str, **params: Any) -> dict:
        response = requests.post(
            f"{self.BASE_URL}{path}",
            params={**self._auth_params(), **params},
            timeout=30,
        )
        self._raise_for_status(response)
        return response.json()

    def put(self, path: str, **params: Any) -> dict:
        response = requests.put(
            f"{self.BASE_URL}{path}",
            params={**self._auth_params(), **params},
            timeout=30,
        )
        self._raise_for_status(response)
        return response.json()

    def get(self, path: str, **params: Any) -> Any:
        response = requests.get(
            f"{self.BASE_URL}{path}",
            params={**self._auth_params(), **params},
            timeout=30,
        )
        self._raise_for_status(response)
        return response.json()

    def delete(self, path: str, **params: Any) -> None:
        response = requests.delete(
            f"{self.BASE_URL}{path}",
            params={**self._auth_params(), **params},
            timeout=30,
        )
        self._raise_for_status(response)

    @staticmethod
    def _raise_for_status(response: requests.Response) -> None:
        if response.ok:
            return
        try:
            detail = response.json()
            message = detail.get("message", response.text)
        except Exception:
            message = response.text
        raise ValidationError(f"Erro Trello API ({response.status_code}): {message}")
