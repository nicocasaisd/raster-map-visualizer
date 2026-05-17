from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routes.overlay import router as overlay_router
from app.routes.tiles import router as tiles_router

app = FastAPI(title="Provider Tile Proxy API", version="0.1.0")

app.include_router(tiles_router)
app.include_router(overlay_router)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
