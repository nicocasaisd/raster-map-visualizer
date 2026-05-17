# Satellite Tile Visualization 

This project is a small tool for visualizing satellite map tiles and experimenting with a basic detection overlay pipeline.

## Directory Structure

```text
raster-map-visualizer/
├── backend/
│   └── app/
│       ├── config.py
│       ├── main.py
│       ├── routes/
│       │   ├── overlay.py
│       │   └── tiles.py
│       └── services/
│           ├── detection.py
│           └── provider.py
└── frontend/
    ├── index.html
    ├── app.js
    └── styles.css
```

## Backend

- Built with FastAPI and Uvicorn.
- Exposes `GET /tiles/{z}/{x}/{y}` for tile proxying and `GET /overlay/{z}/{x}/{y}` for processed overlay tiles.
- Accepts repeated `bidx` query parameters for band selection.
- Uses a provider client service for upstream tile requests and serves frontend static assets.

## Image Processing

- Overlay processing fetches per-band tiles, decodes them to grayscale arrays, and composes a color image tile.
- The detection pipeline logic is included in the codebase and is structured around channel differences, filtering, thresholding, morphology, and connected components.
- Processing is tile-by-tile and returned as PNG bytes.

## Frontend

- Built with Leaflet and vanilla HTML/CSS/JavaScript.
- Renders backend tile endpoints on an interactive map.
- Provides sidebar controls for RGB band selection and overlay mode switching.
- Rebuilds tile layers on control changes while preserving current map position.

## Stack

- Python 3.12
- FastAPI
- Uvicorn
- Requests
- NumPy
- OpenCV (`opencv-python`)
- python-dotenv
- Leaflet
- Vanilla HTML, CSS, and JavaScript
- uv (project/dependency management)
