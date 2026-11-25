"""HTTP JSON API routes for prediction inference and curated sample access."""

import os

from flask import Blueprint, jsonify, request, send_from_directory

from musavision.config import (
    DEFAULT_CONF_THRESHOLD,
    DEFAULT_IOU_THRESHOLD,
    SAMPLES_DIR,
    TEMPLATE_DIR,
    VALID_IMAGE_EXTS,
)
from musavision.services.diagnosis_service import diagnose_leaf_image, list_sample_images

api_bp = Blueprint("api", __name__)


@api_bp.route("/predict", methods=["POST"])
def predict():
    """Accept an uploaded banana leaf image and return diagnosis, FRAC guidance, and telemetry."""
    if "image" not in request.files:
        return jsonify({"status": "error", "message": "Tidak ada file gambar yang dikirimkan."}), 400

    file = request.files["image"]
    if not file.filename:
        return jsonify({"status": "error", "message": "Nama file kosong."}), 400

    conf_threshold = float(request.form.get("conf_threshold", DEFAULT_CONF_THRESHOLD))
    iou_threshold = float(request.form.get("iou_threshold", DEFAULT_IOU_THRESHOLD))
    use_clahe = request.form.get("use_clahe", "true").lower() == "true"

    payload, status_code = diagnose_leaf_image(
        raw_bytes=file.read(),
        filename=file.filename,
        conf_threshold=conf_threshold,
        iou_threshold=iou_threshold,
        use_clahe=use_clahe,
    )
    return jsonify(payload), status_code


@api_bp.route("/api/samples", methods=["GET"])
def get_sample_images():
    """List valid curated sample image URLs across templates and static/samples."""
    samples = list_sample_images()
    return jsonify({"success": True, "samples": samples, "total": len(samples)})


@api_bp.route("/sample-file/<path:filename>", methods=["GET"])
def serve_sample_file(filename: str):
    """Serve allowed sample image files from templates or fallback static/samples."""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in VALID_IMAGE_EXTS:
        return jsonify({"error": "Tipe file tidak diizinkan"}), 403

    target_template = (TEMPLATE_DIR / filename).resolve()
    if str(target_template).startswith(str(TEMPLATE_DIR.resolve())) and target_template.is_file():
        return send_from_directory(TEMPLATE_DIR, filename)

    safe_name = os.path.basename(filename)
    target_static = SAMPLES_DIR / safe_name
    if target_static.is_file():
        return send_from_directory(SAMPLES_DIR, safe_name)

    return jsonify({"error": "File sampel tidak ditemukan", "filename": filename}), 404
