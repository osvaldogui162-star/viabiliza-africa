"""Geocodificação de localização angolana (Google Maps + fallback INE)."""

from __future__ import annotations

import logging
import urllib.parse
import urllib.request
from dataclasses import dataclass

from app.domain.catalog.angola_admin_divisions import resolve_location

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class GeocodeResult:
    latitude: float
    longitude: float
    formatted_address: str
    source: str  # google_maps | ine
    verified: bool


class LocationGeocoder:
    """Valida província/município contra catálogo INE e opcionalmente Google Geocoding API."""

    def __init__(self, *, google_maps_api_key: str | None = None) -> None:
        self._api_key = (google_maps_api_key or "").strip()

    def geocode(
        self,
        *,
        province_code: str,
        municipality_code: str,
        address: str | None = None,
    ) -> GeocodeResult:
        resolved = resolve_location(province_code, municipality_code)
        if resolved is None:
            raise ValueError("Província ou município inválido segundo o catálogo INE")

        municipality, province = resolved
        query_parts = [
            address.strip() if address and address.strip() else None,
            municipality.label,
            province.label,
            "Angola",
        ]
        query = ", ".join(p for p in query_parts if p)

        if self._api_key:
            google = self._try_google(query)
            if google is not None:
                return google

        formatted = query if address else f"{municipality.label}, {province.label}, Angola"
        return GeocodeResult(
            latitude=municipality.latitude,
            longitude=municipality.longitude,
            formatted_address=formatted,
            source="ine",
            verified=True,
        )

    def _try_google(self, query: str) -> GeocodeResult | None:
        try:
            params = urllib.parse.urlencode(
                {"address": query, "key": self._api_key, "region": "ao"}
            )
            url = f"https://maps.googleapis.com/maps/api/geocode/json?{params}"
            with urllib.request.urlopen(url, timeout=8) as response:
                import json

                payload = json.loads(response.read().decode("utf-8"))
            if payload.get("status") != "OK":
                logger.warning("Google Geocoding status: %s", payload.get("status"))
                return None
            result = payload["results"][0]
            location = result["geometry"]["location"]
            return GeocodeResult(
                latitude=float(location["lat"]),
                longitude=float(location["lng"]),
                formatted_address=result.get("formatted_address", query),
                source="google_maps",
                verified=True,
            )
        except Exception as exc:
            logger.warning("Google Geocoding falhou: %s", exc)
            return None
