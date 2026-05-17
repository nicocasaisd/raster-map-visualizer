from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Response
from requests import RequestException

from app.config import get_settings
from app.services.provider import ProviderClient

router = APIRouter(tags=["tiles"])


@router.get("/tiles/{z}/{x}/{y}")
def get_tile(
    z: int,
    x: int,
    y: int,
    scale: int | None = Query(default=None),
    tile_matrix_set_id: str | None = Query(default=None, alias="tileMatrixSetId"),
    bidx: list[str] | None = Query(default=None),
    image_format: str | None = Query(default=None, alias="format"),
) -> Response:
    settings = get_settings()
    client = ProviderClient(settings)

    try:
        tile = client.fetch_tile(
            z,
            x,
            y,
            scale=scale,
            tile_matrix_set_id=tile_matrix_set_id,
            bidx=bidx,
            image_format=image_format,
        )
    except RequestException as exc:
        # Return a clear upstream error to the frontend when the provider call fails.
        raise HTTPException(status_code=502, detail=f"Upstream tile request failed: {exc}") from exc

    # Stream exact image bytes back while preserving provider content type.
    return Response(content=tile.content, media_type=tile.content_type)
