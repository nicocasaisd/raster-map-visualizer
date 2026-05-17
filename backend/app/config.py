from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


# Load values from .env into process env variables.
load_dotenv()


@dataclass(frozen=True)
class Settings:
    satellogic_base_url: str
    satellogic_contract_id: str
    satellogic_bearer_token: str
    satellogic_source_url: str
    satellogic_default_scale: int = 2
    satellogic_default_tile_matrix_set_id: str = "WebMercatorQuad"
    satellogic_default_bidx: list[str] | None = None
    satellogic_default_format: str = "png"
    request_timeout_seconds: int = 30


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_settings() -> Settings:
    return Settings(
        satellogic_base_url=os.getenv(
            "SATELLOGIC_BASE_URL",
            "https://api.satellogic.com/raster/cog/tiles",
        ),
        satellogic_contract_id=_require_env("SATELLOGIC_CONTRACT_ID"),
        satellogic_bearer_token=_require_env("SATELLOGIC_BEARER_TOKEN"),
        satellogic_source_url=_require_env("SATELLOGIC_SOURCE_URL"),
        satellogic_default_scale=int(os.getenv("SATELLOGIC_DEFAULT_SCALE", "2")),
        satellogic_default_tile_matrix_set_id=os.getenv(
            "SATELLOGIC_DEFAULT_TILE_MATRIX_SET_ID",
            "WebMercatorQuad",
        ),
        satellogic_default_bidx=[
            value.strip()
            for value in os.getenv("SATELLOGIC_DEFAULT_BIDX", "1,2,3").split(",")
            if value.strip()
        ],
        satellogic_default_format=os.getenv("SATELLOGIC_DEFAULT_FORMAT", "png"),
        request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30")),
    )
