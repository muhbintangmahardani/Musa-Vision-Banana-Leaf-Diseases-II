"""Pure diagnosis orchestrator combining Gatekeeper, CIE-LAB CLAHE, YOLO26n, and agronomy rules."""

import os
import time
from typing import Any

from musavision.config import (
    DEFAULT_CONF_THRESHOLD,
    DEFAULT_IOU_THRESHOLD,
    DEFAULT_USE_CLAHE,
    FALLBACK_CONF_DROP,
    FALLBACK_MIN_CONF,
    SAMPLES_DIR,
    STANDARD_NON_BANANA_REASON,
    STANDARD_NON_BANANA_TITLE,
    TEMPLATE_DIR,
    VALID_IMAGE_EXTS,
)
from musavision.data.pathology_kb import AGRONOMY_KB, SEVERITY_PRIORITY_ORDER
from musavision.services.gatekeeper_service import (
    validate_image_gatekeeper,
    verify_yolo_boxes_against_raw_pixels,
)
from musavision.services.image_processor import (
    apply_cielab_clahe,
    decode_image_bytes,
    draw_smart_bounding_boxes,
    encode_bgr_to_base64,
    resize_for_inference,
)
from musavision.services.yolo_detector import (
    extract_yolo_detections,
    is_model_loaded,
    run_yolo_inference,
)


def diagnose_leaf_image(
    raw_bytes: bytes,
    filename: str,
    conf_threshold: float = DEFAULT_CONF_THRESHOLD,
    iou_threshold: float = DEFAULT_IOU_THRESHOLD,
    use_clahe: bool = DEFAULT_USE_CLAHE,
) -> tuple[dict[str, Any], int]:
    """Execute end-to-end banana leaf diagnosis and return JSON payload plus HTTP status code."""
    if not is_model_loaded():
        return {
            "status": "error",
            "message": "File model 'models/best_yolo26n_clahe.pt' belum ditemukan di server.",
        }, 500

    raw_bgr = decode_image_bytes(raw_bytes)
    if raw_bgr is None:
        return {"status": "error", "message": "Format gambar tidak dapat dibaca atau rusak."}, 400

    gatekeeper_result = validate_image_gatekeeper(raw_bgr, raw_bytes, filename)
    if not gatekeeper_result["valid"]:
        internal_reason = gatekeeper_result.get("internal_reason") or "Gatekeeper: Proporsi helai daun pisang tidak memadai"
        print(f"[PREDICT] File: '{filename}' | Status: REJECTED | Reason: {internal_reason} | Raw: 0 | Verified: 0")
        return {
            "status": "rejected",
            "rejection_type": "non_banana_leaf",
            "title": STANDARD_NON_BANANA_TITLE,
            "reason": STANDARD_NON_BANANA_REASON,
            "metrics": gatekeeper_result,
        }, 200

    t0 = time.perf_counter()
    resized_bgr = resize_for_inference(raw_bgr)
    clahe_bgr = apply_cielab_clahe(resized_bgr)
    input_for_yolo = clahe_bgr if use_clahe else resized_bgr
    preprocess_ms = (time.perf_counter() - t0) * 1000.0

    t1 = time.perf_counter()
    results = run_yolo_inference(input_for_yolo, conf_threshold=conf_threshold, iou_threshold=iou_threshold)
    inference_nms_ms = (time.perf_counter() - t1) * 1000.0

    t2 = time.perf_counter()
    raw_detections = extract_yolo_detections(results)
    verified_detections = verify_yolo_boxes_against_raw_pixels(resized_bgr, raw_detections)

    # Guard against double-CLAHE contrast washout on already high-contrast field photos
    fallback_infer_ms = 0.0
    if use_clahe and len(verified_detections) == 0:
        fallback_conf = max(FALLBACK_MIN_CONF, conf_threshold - FALLBACK_CONF_DROP)
        t_fb = time.perf_counter()
        fallback_results = run_yolo_inference(
            resized_bgr,
            conf_threshold=fallback_conf,
            iou_threshold=iou_threshold,
        )
        fallback_infer_ms = (time.perf_counter() - t_fb) * 1000.0
        inference_nms_ms += fallback_infer_ms

        fallback_raw = extract_yolo_detections(fallback_results)
        fallback_verified = verify_yolo_boxes_against_raw_pixels(resized_bgr, fallback_raw)
        if len(fallback_verified) > 0:
            verified_detections = fallback_verified
            raw_detections = fallback_raw
            input_for_yolo = resized_bgr

    is_invalid_scene = False
    rejection_detail_internal = ""

    if len(verified_detections) > 0:
        max_det_conf = max(d["confidence_pct"] for d in verified_detections)
        m_solidity = gatekeeper_result.get("solidity", 1.0)
        m_blob = gatekeeper_result.get("living_blob_ratio", 1.0)
        m_largest_blob = gatekeeper_result.get("largest_blob_ratio", 1.0)
        m_living_leaf = gatekeeper_result.get("living_leaf_ratio", 1.0)
        m_whole_leaf = gatekeeper_result.get("botanical_ratio", 1.0)

        if all(d["class_name"] == "Fresh" for d in verified_detections):
            if max_det_conf < 68.0 and m_solidity < 0.60 and m_blob < 0.22:
                is_invalid_scene = True
                rejection_detail_internal = "Pasca-YOLO: Deteksi Fresh pada daun terfragmentasi (bukan lamina pisang)"
        elif (
            (m_whole_leaf < 0.20 and m_living_leaf < 0.16)
            or m_largest_blob < 0.18
            or (m_blob < 0.15 and max_det_conf < 70.0)
        ):
            is_invalid_scene = True
            rejection_detail_internal = (
                "Pasca-YOLO: Deteksi bercak pada latar pemandangan/tanah/kayu "
                f"tanpa lamina utuh (whole={m_whole_leaf*100:.1f}%, blob={m_largest_blob*100:.1f}%)"
            )

    if len(verified_detections) == 0 or is_invalid_scene:
        internal_reason = rejection_detail_internal or (
            "YOLO: 0 deteksi terverifikasi" if len(verified_detections) == 0 else "YOLO: Daun terfragmentasi / non-pisang"
        )
        print(
            f"[PREDICT] File: '{filename}' | Status: REJECTED | Reason: {internal_reason} "
            f"| Raw: {len(raw_detections)} | Verified: {len(verified_detections)}"
        )
        return {
            "status": "rejected",
            "rejection_type": "non_banana_leaf",
            "title": STANDARD_NON_BANANA_TITLE,
            "reason": STANDARD_NON_BANANA_REASON,
            "metrics": {
                "total_detections": 0,
                "raw_detections_count": len(raw_detections),
                "internal_reason": internal_reason,
                "green_yellow_pct": gatekeeper_result.get("green_yellow_pct", 0.0),
                "botanical_pct": gatekeeper_result.get("botanical_pct", 0.0),
            },
        }, 200

    detections: list[dict[str, Any]] = []
    detections_to_draw: list[dict[str, Any]] = []
    lesion_level_count = 0
    leaf_level_count = 0
    class_counts: dict[str, int] = {}

    for idx, d in enumerate(verified_detections):
        d["id"] = idx + 1
        std_cls_name = d["class_name"]
        if "Leaf-Level" in d["granularity"]:
            leaf_level_count += 1
        else:
            lesion_level_count += 1

        class_counts[std_cls_name] = class_counts.get(std_cls_name, 0) + 1
        kb_info = AGRONOMY_KB.get(std_cls_name, AGRONOMY_KB["Fresh"])
        x1, y1, x2, y2 = d["bbox"]
        label_text = f"#{d['id']} {std_cls_name} {d['confidence_pct']:.1f}% ({d['box_area_ratio_pct']:.1f}%)"
        detections_to_draw.append({
            "xyxy": (int(x1), int(y1), int(x2), int(y2)),
            "color": kb_info["bgr_color"],
            "label_text": label_text,
        })
        detections.append(d)

    annotated_bgr = draw_smart_bounding_boxes(input_for_yolo, detections_to_draw)
    orig_b64 = encode_bgr_to_base64(resized_bgr)
    clahe_b64 = encode_bgr_to_base64(clahe_bgr)
    annotated_b64 = encode_bgr_to_base64(annotated_bgr)

    postprocess_ms = max(0.0, ((time.perf_counter() - t2) * 1000.0) - fallback_infer_ms)
    server_total_ms = preprocess_ms + inference_nms_ms + postprocess_ms

    dominant_class = None
    agronomy_advice = None
    if len(detections) > 0:
        detected_classes = {d["class_name"] for d in detections}
        dominant_class = next((c for c in SEVERITY_PRIORITY_ORDER if c in detected_classes), "Fresh")
        agronomy_advice = AGRONOMY_KB.get(dominant_class, AGRONOMY_KB["Fresh"])

    print(
        f"[PREDICT] File: '{filename}' | Status: VALID | Dominant: {dominant_class} "
        f"| Raw: {len(raw_detections)} | Verified: {len(detections)}"
    )

    return {
        "status": "success" if len(detections) > 0 else "no_detection",
        "use_clahe": use_clahe,
        "conf_threshold": conf_threshold,
        "total_detections": len(detections),
        "lesion_level_count": lesion_level_count,
        "leaf_level_count": leaf_level_count,
        "class_counts": class_counts,
        "dominant_class": dominant_class,
        "agronomy": agronomy_advice,
        "detections": detections,
        "telemetry": {
            "preprocess_ms": round(preprocess_ms, 2),
            "inference_nms_ms": round(inference_nms_ms, 2),
            "postprocess_ms": round(postprocess_ms, 2),
            "server_total_ms": round(server_total_ms, 2),
        },
        "images": {
            "original_b64": orig_b64,
            "clahe_b64": clahe_b64,
            "annotated_b64": annotated_b64,
        },
    }, 200


def list_sample_images() -> list[dict[str, str]]:
    """Scan templates and static/samples directories for curated test images."""
    samples: list[dict[str, str]] = []
    seen_names: set[str] = set()

    if TEMPLATE_DIR.exists():
        for root, _, files in os.walk(TEMPLATE_DIR):
            for fname in files:
                ext = os.path.splitext(fname)[1].lower()
                if ext in VALID_IMAGE_EXTS and fname not in seen_names:
                    rel_path = os.path.relpath(os.path.join(root, fname), TEMPLATE_DIR).replace("\\", "/")
                    samples.append({
                        "filename": rel_path,
                        "name": fname,
                        "url": f"/sample-file/{rel_path}",
                        "source": "templates",
                    })
                    seen_names.add(fname)

    if SAMPLES_DIR.exists():
        for fname in os.listdir(SAMPLES_DIR):
            ext = os.path.splitext(fname)[1].lower()
            if ext in VALID_IMAGE_EXTS and fname not in seen_names:
                samples.append({
                    "filename": fname,
                    "name": fname,
                    "url": f"/sample-file/{fname}",
                    "source": "static",
                })
                seen_names.add(fname)

    return samples
