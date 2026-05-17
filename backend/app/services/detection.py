from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from app.services.provider import ProviderClient


@dataclass
class OverlayResult:
    content: bytes
    content_type: str
    candidate_count: int


class InterChannelDisplacementDetector:
    def __init__(self, client: ProviderClient) -> None:
        self._client = client

    @staticmethod
    def _decode_to_gray(image_bytes: bytes) -> np.ndarray:
        encoded = np.frombuffer(image_bytes, dtype=np.uint8)
        decoded = cv2.imdecode(encoded, cv2.IMREAD_UNCHANGED)
        if decoded is None:
            raise ValueError("Failed to decode upstream band image")

        if decoded.ndim == 2:
            return decoded

        # Handle 3 or 4 channel responses by converting to a single grayscale band.
        if decoded.shape[2] == 4:
            return cv2.cvtColor(decoded, cv2.COLOR_BGRA2GRAY)
        return cv2.cvtColor(decoded, cv2.COLOR_BGR2GRAY)

    def build_overlay(self, z: int, x: int, y: int) -> OverlayResult:
        # Fetch each band independently so the detector can compare channels.
        band_images: dict[int, np.ndarray] = {}
        for band_idx in (1, 2, 3, 4):
            tile = self._client.fetch_tile(z, x, y, bidx=[str(band_idx)], image_format="png")
            band_images[band_idx] = self._decode_to_gray(tile.content)

        bid1 = band_images[1]
        bid2 = band_images[2]
        bid3 = band_images[3]
        bid4 = band_images[4]

        # OpenCV uses BGR channel order for image operations.
        color = cv2.merge([bid3, bid2, bid1])

        # MVP detection pipeline adapted from the notebook.
        rg = cv2.subtract(bid2, bid1)
        gb = cv2.subtract(bid2, bid3)
        rn = cv2.subtract(bid1, bid4)

        motion_f = rg.astype(np.float32) + gb.astype(np.float32) + rn.astype(np.float32)
        motion = cv2.normalize(motion_f, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        motion = cv2.GaussianBlur(motion, (5, 5), 0)

        _, thresh = cv2.threshold(motion, 60, 255, cv2.THRESH_BINARY)

        kernel = np.ones((3, 3), np.uint8)
        clean = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        clean = cv2.dilate(clean, kernel, iterations=3)

        num_labels, _, stats, _ = cv2.connectedComponentsWithStats(clean, connectivity=8)
        min_area = 8
        max_area = 2000

        candidate_count = 0
        if num_labels < 20:
            for label in range(1, num_labels):
                x0, y0, w, h, area = stats[label]
                if min_area <= area <= max_area:
                    candidate_count += 1
                    cv2.rectangle(color, (x0, y0), (x0 + w, y0 + h), (0, 255, 255), 1)

        ok, encoded = cv2.imencode(".png", color)
        if not ok:
            raise ValueError("Failed to encode overlay PNG")

        return OverlayResult(
            content=encoded.tobytes(),
            content_type="image/png",
            candidate_count=candidate_count,
        )
