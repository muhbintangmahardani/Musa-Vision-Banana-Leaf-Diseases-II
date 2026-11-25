"""Pure image decoding, CIE-LAB CLAHE enhancement, bounding box drawing, and encoding."""

import base64
import io
from typing import Any, Optional

import cv2
import numpy as np
from PIL import Image, ImageOps

from musavision.config import (
    CLAHE_CLIP_LIMIT,
    CLAHE_TILE_SIZE,
    JPEG_OUTPUT_QUALITY,
    YOLO_IMAGE_SIZE,
)


def decode_image_bytes(raw_bytes: bytes) -> Optional[np.ndarray]:
    """Decode uploaded image bytes to BGR format while honoring EXIF camera orientation."""
    try:
        pil_img = Image.open(io.BytesIO(raw_bytes))
        pil_img = ImageOps.exif_transpose(pil_img).convert("RGB")
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    except Exception:
        file_bytes = np.frombuffer(raw_bytes, np.uint8)
        return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)


def resize_for_inference(img_bgr: np.ndarray, size: int = YOLO_IMAGE_SIZE) -> np.ndarray:
    """Resize BGR image to square inference resolution expected by YOLO26n."""
    return cv2.resize(img_bgr, (size, size), interpolation=cv2.INTER_LINEAR)


def apply_cielab_clahe(
    img_bgr_640: np.ndarray,
    clip_limit: float = CLAHE_CLIP_LIMIT,
    tile_size: int = CLAHE_TILE_SIZE,
) -> np.ndarray:
    """Enhance local micro-contrast purely on the CIE-LAB luminance (L) channel."""
    lab_img = cv2.cvtColor(img_bgr_640, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab_img)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
    l_enhanced = clahe.apply(l_channel)
    merged_lab = cv2.merge((l_enhanced, a_channel, b_channel))
    return cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)


def draw_smart_bounding_boxes(
    img_bgr: np.ndarray,
    detections_to_draw: list[dict[str, Any]],
) -> np.ndarray:
    """Draw bounding boxes and collision-avoiding badge labels clamped inside canvas bounds."""
    canvas = img_bgr.copy()
    h, w = canvas.shape[:2]
    occupied_label_rects: list[tuple[int, int, int, int]] = []

    for item in detections_to_draw:
        x1, y1, x2, y2 = item["xyxy"]
        cv2.rectangle(canvas, (x1, y1), (x2, y2), item["color"], 2)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.50
    thickness = 2

    for item in detections_to_draw:
        x1, y1, x2, y2 = item["xyxy"]
        color = item["color"]
        label_text = item["label_text"]

        (tw, th), baseline = cv2.getTextSize(label_text, font, font_scale, thickness)
        box_h_pad = th + baseline + 8
        box_w_pad = tw + 10

        lx1 = max(2, min(x1, w - box_w_pad - 2))
        lx2 = lx1 + box_w_pad

        if y1 - box_h_pad >= 4:
            ly1 = y1 - box_h_pad
            ly2 = y1
        else:
            ly1 = max(2, y1 + 2)
            ly2 = ly1 + box_h_pad

        for ox1, oy1, ox2, oy2 in occupied_label_rects:
            if not (lx2 < ox1 or lx1 > ox2) and not (ly2 < oy1 or ly1 > oy2):
                ly1 = min(h - box_h_pad - 2, oy2 + 3)
                ly2 = ly1 + box_h_pad

        occupied_label_rects.append((lx1, ly1, lx2, ly2))
        cv2.rectangle(canvas, (lx1, ly1), (lx2, ly2), color, -1)
        cv2.rectangle(canvas, (lx1, ly1), (lx2, ly2), (255, 255, 255), 1)
        cv2.putText(
            canvas,
            label_text,
            (lx1 + 5, ly1 + th + 4),
            font,
            font_scale,
            (255, 255, 255),
            thickness,
            cv2.LINE_AA,
        )

    return canvas


def encode_bgr_to_base64(img_bgr: np.ndarray) -> str:
    """Encode BGR matrix into a JPEG data-URI base64 string for frontend display."""
    _, buffer = cv2.imencode(".jpg", img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_OUTPUT_QUALITY])
    return f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"
