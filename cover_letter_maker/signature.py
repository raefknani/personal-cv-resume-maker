from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import numpy as np
from PIL import Image, ImageOps


@dataclass
class ProcessedSignature:
    png_bytes: bytes
    width: int
    height: int
    confidence: float
    warnings: list[str]
    processing_mode: str


class SignatureProcessor:
    def __init__(self, max_bytes: int = 10 * 1024 * 1024, max_dimension: int = 12000):
        self.max_bytes = max_bytes
        self.max_dimension = max_dimension

    def process_upload(self, image_bytes: bytes) -> ProcessedSignature:
        return self._process(image_bytes, "direct_upload")

    def process_template_scan(self, image_bytes: bytes) -> ProcessedSignature:
        return self._process(image_bytes, "template_scan")

    def _process(self, image_bytes: bytes, mode: str) -> ProcessedSignature:
        if len(image_bytes) > self.max_bytes:
            raise ValueError("Image must be smaller than 10 MB")
        if not image_bytes.startswith((b"\x89PNG", b"\xff\xd8\xff")):
            raise ValueError("Only PNG and JPEG images are supported")
        try:
            image = ImageOps.exif_transpose(Image.open(io.BytesIO(image_bytes))).convert("RGBA")
        except Exception as exc:
            raise ValueError(f"Could not decode image: {exc}") from exc
        if max(image.size) > self.max_dimension:
            image.thumbnail((self.max_dimension, self.max_dimension), Image.Resampling.LANCZOS)
        array = np.asarray(image)
        rgb = array[:, :, :3].astype(np.uint16)
        brightness = rgb.mean(axis=2)
        alpha = np.where(brightness < 225, np.clip((225 - brightness) * 3, 0, 255), 0).astype(np.uint8)
        alpha[brightness < 80] = 255
        ys, xs = np.where(alpha > 10)
        warnings: list[str] = []
        if len(xs) == 0:
            raise ValueError("No signature strokes were detected")
        if len(xs) < 30:
            warnings.append("Very little foreground was detected; please verify the preview.")
        pad = max(3, min(image.size) // 100)
        left, right = max(0, xs.min() - pad), min(image.width, xs.max() + pad + 1)
        top, bottom = max(0, ys.min() - pad), min(image.height, ys.max() + pad + 1)
        rgba = np.zeros((bottom - top, right - left, 4), dtype=np.uint8)
        rgba[:, :, 3] = alpha[top:bottom, left:right]
        output = io.BytesIO()
        Image.fromarray(rgba, "RGBA").save(output, format="PNG", optimize=True)
        return ProcessedSignature(output.getvalue(), rgba.shape[1], rgba.shape[0], 0.9 if mode == "template_scan" else 0.82, warnings, mode)


class TemporarySignatureStorage:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, result: ProcessedSignature) -> dict:
        asset_id = f"tmp_{uuid4().hex}"
        path = self.root / f"{asset_id}.png"
        path.write_bytes(result.png_bytes)
        return {"signature_id": asset_id, "path": str(path), "width": result.width, "height": result.height, "confidence": result.confidence, "warnings": result.warnings, "processing_mode": result.processing_mode}