"""Singleton loader and pure inference wrapper for the YOLO26 Nano model."""

import os
from typing import Any, Optional

import numpy as np
from ultralytics import YOLO

from musavision.config import BASE_DIR, MODEL_PATHS, YOLO_IMAGE_SIZE
from musavision.data.pathology_kb import normalize_class_name

_model: Optional[YOLO] = None
_loaded_model_path: Optional[str] = None
_initialized: bool = False


def get_model() -> Optional[YOLO]:
    """Return the cached YOLO model instance, loading weights lazily on first call."""
    global _model, _loaded_model_path, _initialized
    if _initialized:
        return _model

    _initialized = True
    for candidate in MODEL_PATHS:
        if candidate.exists():
            _model = YOLO(str(candidate))
            _loaded_model_path = os.path.relpath(candidate, BASE_DIR)
            print(f"[INFO] Model penyakit daun berhasil dimuat dari: {_loaded_model_path}")
            return _model

    print("[WARNING] File 'models/best_yolo26n_clahe.pt' belum ditemukan!")
    return None


def is_model_loaded() -> bool:
    """Return True if the YOLO weights have been loaded into memory."""
    return get_model() is not None


def get_loaded_model_path() -> Optional[str]:
    """Return the relative filesystem path of the active YOLO weights file."""
    get_model()
    return _loaded_model_path


def run_yolo_inference(
    image_bgr: np.ndarray,
    conf_threshold: float,
    iou_threshold: float,
    imgsz: int = YOLO_IMAGE_SIZE,
) -> Any:
    """Run YOLO object detection on a BGR image matrix without file I/O."""
    model = get_model()
    if model is None:
        raise RuntimeError("YOLO model weights are not loaded.")

    return model.predict(
        source=image_bgr,
        imgsz=imgsz,
        conf=conf_threshold,
        iou=iou_threshold,
        verbose=False,
    )


def extract_yolo_detections(results: Any) -> list[dict[str, Any]]:
    """Convert raw Ultralytics box predictions into standardized detection records."""
    raw_detections: list[dict[str, Any]] = []
    result = results[0]
    boxes = result.boxes
    names = result.names

    if boxes is not None and len(boxes) > 0:
        for idx, box in enumerate(boxes):
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().tolist()
            conf = float(box.conf[0].cpu().numpy())
            cls_id = int(box.cls[0].cpu().numpy())
            raw_cls_name = names.get(cls_id, str(cls_id))
            std_cls_name = normalize_class_name(raw_cls_name)

            box_w = max(0.0, x2 - x1)
            box_h = max(0.0, y2 - y1)
            area_ratio_pct = ((box_w * box_h) / float(YOLO_IMAGE_SIZE * YOLO_IMAGE_SIZE)) * 100.0

            granularity = (
                "Leaf-Level (Cakupan Helai Daun)"
                if (std_cls_name in ["Fresh", "Yellow Sigatoka"] or area_ratio_pct >= 35.0)
                else "Lesion-Level (Titik Bercak)"
            )

            raw_detections.append({
                "id": idx + 1,
                "class_name": std_cls_name,
                "confidence_pct": round(conf * 100.0, 2),
                "box_area_ratio_pct": round(area_ratio_pct, 2),
                "granularity": granularity,
                "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)],
            })

    return raw_detections
