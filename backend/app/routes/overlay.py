from __future__ import annotations

from fastapi import APIRouter, HTTPException, Response
from requests import RequestException

from app.config import get_settings
from app.services.detection import InterChannelDisplacementDetector
from app.services.provider import ProviderClient

router = APIRouter(tags=["overlay"])


@router.get("/overlay/{z}/{x}/{y}")
def get_overlay_tile(z: int, x: int, y: int) -> Response:
    settings = get_settings()
    client = ProviderClient(settings)
    detector = InterChannelDisplacementDetector(client)

    try:
        overlay = detector.build_overlay(z, x, y)
    except RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Upstream tile request failed: {exc}") from exc
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=f"Overlay generation failed: {exc}") from exc

    return Response(content=overlay.content, media_type=overlay.content_type)
