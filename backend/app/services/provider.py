from __future__ import annotations

from dataclasses import dataclass

import requests

from app.config import Settings


@dataclass
class TileResponse:
    content: bytes
    content_type: str


class ProviderClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._session = requests.Session()

    def fetch_tile(
        self,
        z: int,
        x: int,
        y: int,
        *,
        scale: int | None = None,
        tile_matrix_set_id: str | None = None,
        bidx: list[str] | None = None,
        image_format: str | None = None,
    ) -> TileResponse:
        # Adapter to isolate HTTP requests
        endpoint = f"{self._settings.satellogic_base_url}/{z}/{x}/{y}"

        params = {
            "scale": scale or self._settings.satellogic_default_scale,
            "tileMatrixSetId": tile_matrix_set_id
            or self._settings.satellogic_default_tile_matrix_set_id,
            "url": self._settings.satellogic_source_url,
            # requests encodes list values as repeated query params:
            # bidx=1&bidx=2&bidx=3
            "bidx": bidx if bidx is not None else self._settings.satellogic_default_bidx,
            "format": image_format or self._settings.satellogic_default_format,
        }
        headers = {
            "authorizationToken": f"Bearer {self._settings.satellogic_bearer_token}",
            "X-Satellogic-Contract-Id": self._settings.satellogic_contract_id,
            "Accept": "*/*",
            "User-Agent": "sat-tiles-api/0.1",
            "Referer": "https://aleph.satellogic.com/",
            "Origin": "https://aleph.satellogic.com",
        }

        response = self._session.get(
            endpoint,
            params=params,
            headers=headers,
            timeout=self._settings.request_timeout_seconds,
        )
        response.raise_for_status()

        return TileResponse(
            content=response.content,
            content_type=response.headers.get("content-type", "application/octet-stream"),
        )
