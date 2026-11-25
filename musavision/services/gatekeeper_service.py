"""Multi-layer Gatekeeper validating genuine banana leaves before and after YOLO inference."""

import io
from typing import Any

import cv2
import numpy as np
from PIL import ExifTags, Image

from musavision.config import (
    AI_DIFFUSION_PARAM_TERMS,
    AI_FILENAME_KEYWORDS,
    AI_METADATA_KEYWORDS,
    EXACT_AI_RESOLUTIONS,
    HSV_GREEN_LOWER,
    HSV_GREEN_UPPER,
    HSV_NECROTIC_LOWER,
    HSV_NECROTIC_UPPER,
    HSV_PALE_DRY_LOWER,
    HSV_PALE_DRY_UPPER,
    HSV_PITCH_DARK_LOWER,
    HSV_PITCH_DARK_UPPER,
    HSV_ROI_DARK_LOWER,
    HSV_ROI_DARK_UPPER,
    HSV_ROI_NECROTIC_LOWER,
    HSV_ROI_NECROTIC_UPPER,
    HSV_SKIN_LOWER,
    HSV_SKIN_UPPER,
    HSV_SPECULAR_LOWER,
    HSV_SPECULAR_UPPER,
    HSV_WATER_BLUE_LOWER,
    HSV_WATER_BLUE_UPPER,
    HSV_YELLOW_LOWER,
    HSV_YELLOW_UPPER,
    LEAF_CONFUSION_CATEGORIES,
    POT_AND_OTHER_PLANT_KEYWORDS,
    POT_SENSITIVE_KEYWORDS,
    REJECTED_NON_LEAF_KEYWORDS,
    STANDARD_NON_BANANA_REASON,
    STANDARD_NON_BANANA_TITLE,
    YCRCB_SKIN_LOWER,
    YCRCB_SKIN_UPPER,
    YOLO_IMAGE_SIZE,
)

# Optional Torchvision MobileNetV3 for semantic non-leaf object screening
try:
    import torch
    from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small

    IMAGENET_WEIGHTS = MobileNet_V3_Small_Weights.DEFAULT
    IMAGENET_MODEL = mobilenet_v3_small(weights=IMAGENET_WEIGHTS).eval()
    IMAGENET_PREPROCESS = IMAGENET_WEIGHTS.transforms()
    IMAGENET_CATEGORIES = IMAGENET_WEIGHTS.meta["categories"]
    HAS_IMAGENET_GUARD = True
except Exception as exc:
    HAS_IMAGENET_GUARD = False
    IMAGENET_MODEL = None
    IMAGENET_PREPROCESS = None
    IMAGENET_CATEGORIES = []
    print(f"[INFO] ImageNet Guard tidak aktif ({exc}), menggunakan OpenCV Gatekeeper.")

FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
FACE_ALT_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"
)
HOG_PEOPLE_DETECTOR = cv2.HOGDescriptor()
HOG_PEOPLE_DETECTOR.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())


def _compute_skin_mask(hsv: np.ndarray, ycrcb: np.ndarray) -> np.ndarray:
    mask_ycrcb = cv2.inRange(ycrcb, np.array(YCRCB_SKIN_LOWER), np.array(YCRCB_SKIN_UPPER))
    mask_hsv = cv2.inRange(hsv, np.array(HSV_SKIN_LOWER), np.array(HSV_SKIN_UPPER))
    return cv2.bitwise_and(mask_ycrcb, mask_hsv)


def _compute_leaf_spectrum_masks(hsv: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mask_green = cv2.inRange(hsv, np.array(HSV_GREEN_LOWER), np.array(HSV_GREEN_UPPER))
    mask_yellow = cv2.inRange(hsv, np.array(HSV_YELLOW_LOWER), np.array(HSV_YELLOW_UPPER))
    mask_necrotic = cv2.inRange(hsv, np.array(HSV_NECROTIC_LOWER), np.array(HSV_NECROTIC_UPPER))
    mask_lamina = cv2.bitwise_or(mask_green, mask_yellow)
    mask_whole = cv2.bitwise_or(mask_lamina, mask_necrotic)
    return mask_green, mask_yellow, mask_necrotic, mask_lamina, mask_whole


def detect_ai_generated_image(file_bytes: bytes, filename: str, img_bgr: np.ndarray) -> dict[str, Any]:
    """Detect synthetic AI-generated imagery via filename traces, C2PA/PNG/EXIF metadata, and smoothness."""
    fname_lower = (filename or "").lower()
    for kw in AI_FILENAME_KEYWORDS:
        if kw in fname_lower:
            return {
                "is_ai": True,
                "reason": (
                    f"Terdeteksi Gambar Hasil Generate AI (Jejak nama file: '{kw}'). "
                    "Sistem MusaVision hanya memproses foto daun pisang asli dari kebun/kamera, "
                    "bukan citra sintetis buatan AI."
                ),
            }

    binary_sample = file_bytes[:131072] + (file_bytes[-65536:] if len(file_bytes) > 65536 else b"")
    raw_latin = binary_sample.decode("latin-1", errors="ignore").lower()
    for kw in AI_METADATA_KEYWORDS:
        if kw in raw_latin:
            return {
                "is_ai": True,
                "reason": (
                    f"Terdeteksi Gambar Hasil Generate AI (Metadata C2PA/XMP/Software mengandung '{kw}'). "
                    "Citra sintetis buatan AI memiliki pola pencahayaan buatan yang tidak valid untuk diagnosis penyakit."
                ),
            }

    has_camera_exif = False
    try:
        pil_img = Image.open(io.BytesIO(file_bytes))

        if hasattr(pil_img, "info") and isinstance(pil_img.info, dict):
            for k, v in pil_img.info.items():
                k_lower = str(k).lower()
                v_lower = str(v).lower()
                if any(kw in k_lower or kw in v_lower for kw in AI_METADATA_KEYWORDS):
                    return {
                        "is_ai": True,
                        "reason": f"Terdeteksi Gambar Hasil Generate AI pada metadata teks PNG ({k}).",
                    }
                if k_lower in ["parameters", "prompt", "workflow"] and any(
                    term in v_lower for term in AI_DIFFUSION_PARAM_TERMS
                ):
                    return {
                        "is_ai": True,
                        "reason": f"Terdeteksi Gambar Hasil Generate AI pada metadata alur kerja difusi ({k}).",
                    }

        exif_dict: dict[str, str] = {}
        if hasattr(pil_img, "getexif"):
            exif_obj = pil_img.getexif()
            if exif_obj:
                for tag_id, val in exif_obj.items():
                    tag_name = str(ExifTags.TAGS.get(tag_id, tag_id)).lower()
                    exif_dict[tag_name] = str(val)
                try:
                    if hasattr(ExifTags, "IFD") and hasattr(ExifTags.IFD, "Exif"):
                        sub_exif = exif_obj.get_ifd(ExifTags.IFD.Exif)
                        for tag_id, val in sub_exif.items():
                            tag_name = str(ExifTags.TAGS.get(tag_id, tag_id)).lower()
                            exif_dict[tag_name] = str(val)
                except Exception:
                    pass
        if not exif_dict and hasattr(pil_img, "_getexif"):
            raw_exif = pil_img._getexif()
            if raw_exif:
                for tag_id, val in raw_exif.items():
                    tag_name = str(ExifTags.TAGS.get(tag_id, tag_id)).lower()
                    exif_dict[tag_name] = str(val)

        for tag_name, val_str in exif_dict.items():
            val_lower = val_str.lower()
            if any(k in val_lower for k in AI_METADATA_KEYWORDS):
                return {
                    "is_ai": True,
                    "reason": f"Terdeteksi Gambar Hasil Generate AI pada atribut EXIF Software ('{val_str}').",
                }
            if tag_name in ["make", "model", "lensmodel", "focallength", "isospeedratings", "datetimeoriginal"]:
                if len(val_str.strip()) > 1:
                    has_camera_exif = True
    except Exception:
        pass

    if has_camera_exif:
        return {"is_ai": False, "reason": "Memiliki EXIF kamera asli."}

    h, w = img_bgr.shape[:2]
    is_dataset_size = (w == YOLO_IMAGE_SIZE and h == YOLO_IMAGE_SIZE)

    if (w, h) in EXACT_AI_RESOLUTIONS and not is_dataset_size:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
        lap_var = float(np.var(cv2.Laplacian(gray, cv2.CV_32F)))
        blur_diff = np.abs(gray - cv2.GaussianBlur(gray, (5, 5), 0))
        hyper_smooth_ratio = float(np.mean(blur_diff < 1.8))

        if hyper_smooth_ratio > 0.96 and lap_var < 15.0:
            return {
                "is_ai": True,
                "reason": (
                    f"Terdeteksi Gambar Hasil Generate AI (Resolusi sintetis {w}\u00d7{h} tanpa EXIF kamera "
                    "dengan tekstur permukaan plastis/airbrushed tanpa serat urat daun alami)."
                ),
            }

    return {"is_ai": False, "reason": "Bukan citra AI."}


def analyze_banana_vs_other_leaf(
    img_bgr: np.ndarray,
    mask_whole_leaf: np.ndarray,
    mask_leaf_lamina: np.ndarray,
) -> dict[str, Any]:
    """Screen semantic scene class via MobileNetV3 and compute leaf contour cohesion metrics."""
    h, w = img_bgr.shape[:2]
    total_pixels = float(h * w)
    living_leaf_ratio = np.count_nonzero(mask_leaf_lamina) / total_pixels

    if HAS_IMAGENET_GUARD and IMAGENET_MODEL is not None:
        try:
            rgb_pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
            input_tensor = IMAGENET_PREPROCESS(rgb_pil).unsqueeze(0)
            with torch.no_grad():
                logits = IMAGENET_MODEL(input_tensor)
                probs = torch.nn.functional.softmax(logits[0], dim=0)
                top10_prob, top10_catid = torch.topk(probs, 10)

            non_leaf_score_sum = 0.0
            matched_non_leaf_names: list[str] = []
            for i in range(10):
                cat_name = IMAGENET_CATEGORIES[top10_catid[i]].lower()
                prob_val = float(top10_prob[i].item())
                if (
                    any(kw in cat_name for kw in REJECTED_NON_LEAF_KEYWORDS)
                    and cat_name not in LEAF_CONFUSION_CATEGORIES
                ):
                    non_leaf_score_sum += prob_val
                    matched_non_leaf_names.append(f"{cat_name} {prob_val*100:.1f}%")
                    is_clear_non_leaf = (living_leaf_ratio < 0.65 and prob_val >= 0.05) or (prob_val >= 0.22)
                    if is_clear_non_leaf:
                        return {
                            "is_non_leaf_object": True,
                            "title": STANDARD_NON_BANANA_TITLE,
                            "reason": STANDARD_NON_BANANA_REASON,
                            "internal_reason": f"ImageNet semantik non-daun: {cat_name} ({prob_val*100:.1f}%)",
                            "largest_blob_ratio": 0.0,
                            "living_blob_ratio": 0.0,
                            "solidity": 0.0,
                            "num_blobs": 0,
                        }

            if (living_leaf_ratio < 0.65 and non_leaf_score_sum >= 0.10) or (
                living_leaf_ratio >= 0.65 and non_leaf_score_sum >= 0.50
            ):
                return {
                    "is_non_leaf_object": True,
                    "title": STANDARD_NON_BANANA_TITLE,
                    "reason": STANDARD_NON_BANANA_REASON,
                    "internal_reason": (
                        f"ImageNet skor non-daun kumulatif tinggi ({non_leaf_score_sum*100:.1f}%): "
                        f"{', '.join(matched_non_leaf_names)}"
                    ),
                    "largest_blob_ratio": 0.0,
                    "living_blob_ratio": 0.0,
                    "solidity": 0.0,
                    "num_blobs": 0,
                }

            for i in range(10):
                cat_name = IMAGENET_CATEGORIES[top10_catid[i]].lower()
                prob_val = float(top10_prob[i].item())
                if cat_name in LEAF_CONFUSION_CATEGORIES:
                    continue
                for kw in POT_AND_OTHER_PLANT_KEYWORDS:
                    threshold = 0.05 if kw in POT_SENSITIVE_KEYWORDS else 0.15
                    if kw in cat_name and prob_val >= threshold:
                        return {
                            "is_other_leaf": True,
                            "title": STANDARD_NON_BANANA_TITLE,
                            "reason": STANDARD_NON_BANANA_REASON,
                            "internal_reason": f"ImageNet terdeteksi wadah/pot/tanaman non-pisang: {cat_name} ({prob_val*100:.1f}%)",
                            "largest_blob_ratio": 0.0,
                            "living_blob_ratio": 0.0,
                            "solidity": 0.0,
                            "num_blobs": 0,
                        }
        except Exception:
            pass

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    closed_whole = cv2.morphologyEx(mask_whole_leaf, cv2.MORPH_CLOSE, kernel)
    contours_whole, _ = cv2.findContours(closed_whole, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    closed_living = cv2.morphologyEx(mask_leaf_lamina, cv2.MORPH_CLOSE, kernel)
    contours_living, _ = cv2.findContours(closed_living, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours_whole or not contours_living:
        return {
            "is_other_leaf": False,
            "largest_blob_ratio": 0.0,
            "living_blob_ratio": 0.0,
            "solidity": 0.0,
            "num_blobs": 0,
        }

    largest_cnt = max(contours_whole, key=cv2.contourArea)
    largest_area = float(cv2.contourArea(largest_cnt))
    largest_blob_ratio = largest_area / total_pixels

    largest_living_cnt = max(contours_living, key=cv2.contourArea)
    living_blob_ratio = float(cv2.contourArea(largest_living_cnt)) / total_pixels

    hull = cv2.convexHull(largest_cnt)
    hull_area = float(cv2.contourArea(hull))
    solidity = largest_area / (hull_area + 1e-5)

    significant_blobs = [c for c in contours_living if (cv2.contourArea(c) / total_pixels) >= 0.02]

    return {
        "is_other_leaf": False,
        "largest_blob_ratio": largest_blob_ratio,
        "living_blob_ratio": living_blob_ratio,
        "solidity": solidity,
        "num_blobs": len(significant_blobs),
    }


def _build_rejection_payload(
    rejection_type: str,
    internal_reason: str,
    living_leaf_ratio: float,
    botanical_ratio: float,
) -> dict[str, Any]:
    return {
        "valid": False,
        "rejection_type": rejection_type,
        "title": STANDARD_NON_BANANA_TITLE,
        "reason": STANDARD_NON_BANANA_REASON,
        "internal_reason": internal_reason,
        "green_yellow_pct": round(living_leaf_ratio * 100, 2),
        "botanical_pct": round(botanical_ratio * 100, 2),
    }


def validate_image_gatekeeper(img_bgr: np.ndarray, file_bytes: bytes, filename: str) -> dict[str, Any]:
    """Run pre-YOLO Gatekeeper filtering AI renders, plastic leaves, humans, water/sky, pots, and bare soil."""
    h, w = img_bgr.shape[:2]
    total_pixels = float(h * w)

    ai_check = detect_ai_generated_image(file_bytes, filename, img_bgr)
    if ai_check["is_ai"]:
        return {
            "valid": False,
            "rejection_type": "ai_generated",
            "title": STANDARD_NON_BANANA_TITLE,
            "reason": STANDARD_NON_BANANA_REASON,
            "internal_reason": f"AI-Generated Image: {ai_check['reason']}",
            "green_yellow_pct": 0.0,
            "botanical_pct": 0.0,
        }

    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    ycrcb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    mask_skin = _compute_skin_mask(hsv, ycrcb)
    skin_ratio = np.count_nonzero(mask_skin) / total_pixels

    mask_true_green, mask_yellow, mask_necrotic, mask_leaf_lamina, mask_whole_leaf = (
        _compute_leaf_spectrum_masks(hsv)
    )
    true_green_ratio = np.count_nonzero(mask_true_green) / total_pixels
    yellow_ratio = np.count_nonzero(mask_yellow) / total_pixels
    necrotic_ratio = np.count_nonzero(mask_necrotic) / total_pixels
    living_leaf_ratio = true_green_ratio + yellow_ratio
    botanical_ratio = np.count_nonzero(mask_whole_leaf) / total_pixels

    mask_pitch_dark = cv2.inRange(hsv, np.array(HSV_PITCH_DARK_LOWER), np.array(HSV_PITCH_DARK_UPPER))
    pitch_dark_ratio = np.count_nonzero(mask_pitch_dark) / total_pixels

    mask_specular = cv2.inRange(hsv, np.array(HSV_SPECULAR_LOWER), np.array(HSV_SPECULAR_UPPER))
    specular_ratio = np.count_nonzero(mask_specular) / total_pixels

    # Reject uniform synthetic plastic foliage before biometric checks
    green_pixels = np.count_nonzero(mask_true_green)
    if green_pixels > 500:
        hue_std = float(np.std(hsv[mask_true_green > 0, 0]))
        sat_std = float(np.std(hsv[mask_true_green > 0, 1]))
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        is_synthetic = (
            (specular_ratio >= 0.05 and hue_std < 4.0 and lap_var < 35.0)
            or (hue_std < 1.8 and sat_std < 15.0 and true_green_ratio >= 0.20)
        )
        if is_synthetic:
            return _build_rejection_payload(
                "non_banana_leaf",
                "Daun sintetis / plastik (lap_var rendah & spekular tinggi)",
                living_leaf_ratio,
                botanical_ratio,
            )

    min_face = (max(20, int(min(w, h) * 0.04)), max(20, int(min(w, h) * 0.04)))
    detected_faces = (
        list(FACE_CASCADE.detectMultiScale(gray, 1.1, 4, minSize=min_face))
        + list(FACE_ALT_CASCADE.detectMultiScale(gray, 1.1, 4, minSize=min_face))
    )
    verified_faces = []
    for fx, fy, fw, fh in detected_faces:
        roi_ycrcb = ycrcb[fy : fy + fh, fx : fx + fw]
        roi_hsv = hsv[fy : fy + fh, fx : fx + fw]
        face_skin_r = np.count_nonzero(_compute_skin_mask(roi_hsv, roi_ycrcb)) / float(fw * fh)
        face_green_r = (
            np.count_nonzero(cv2.inRange(roi_hsv, np.array(HSV_GREEN_LOWER), np.array(HSV_GREEN_UPPER)))
            / float(fw * fh)
        )
        if face_skin_r >= 0.20 and face_green_r < 0.35:
            verified_faces.append((fx, fy, fw, fh))

    if len(verified_faces) > 0 and living_leaf_ratio < 0.70:
        return _build_rejection_payload(
            "non_banana_leaf",
            f"Terdeteksi wajah manusia ({len(verified_faces)} wajah terverifikasi)",
            living_leaf_ratio,
            botanical_ratio,
        )

    if living_leaf_ratio < 0.55:
        scale_w = max(128, min(480, w))
        scale_h = max(160, int(h * (scale_w / float(w))))
        small_bgr = cv2.resize(img_bgr, (scale_w, scale_h))
        _, weights = HOG_PEOPLE_DETECTOR.detectMultiScale(
            small_bgr, winStride=(8, 8), padding=(8, 8), scale=1.05
        )
        strong_people = [float(wt) for wt in np.ravel(weights) if float(wt) >= 0.45] if len(weights) > 0 else []
        if len(strong_people) > 0:
            return _build_rejection_payload(
                "non_banana_leaf",
                f"Siluet tubuh manusia terdeteksi (HOG weights={strong_people})",
                living_leaf_ratio,
                botanical_ratio,
            )

    if (skin_ratio >= 0.15 and living_leaf_ratio < 0.40) or (skin_ratio >= 0.08 and living_leaf_ratio < 0.25):
        return _build_rejection_payload(
            "non_banana_leaf",
            f"Dominasi warna kulit manusia ({skin_ratio*100:.1f}%)",
            living_leaf_ratio,
            botanical_ratio,
        )

    mask_water_blue = cv2.inRange(hsv, np.array(HSV_WATER_BLUE_LOWER), np.array(HSV_WATER_BLUE_UPPER))
    water_blue_ratio = np.count_nonzero(mask_water_blue) / total_pixels
    if water_blue_ratio >= 0.035 and living_leaf_ratio < 0.65:
        return _build_rejection_payload(
            "non_banana_leaf",
            f"Unsur air/langit terbuka di pemandangan ({water_blue_ratio*100:.1f}%)",
            living_leaf_ratio,
            botanical_ratio,
        )

    morph_info = analyze_banana_vs_other_leaf(img_bgr, mask_whole_leaf, mask_leaf_lamina)

    if morph_info.get("is_other_leaf"):
        return _build_rejection_payload(
            "non_banana_leaf",
            morph_info.get("internal_reason", "Morfologi tanaman lain / wadah pot"),
            living_leaf_ratio,
            botanical_ratio,
        )

    if morph_info.get("is_non_leaf_object"):
        return _build_rejection_payload(
            "non_banana_leaf",
            morph_info.get("internal_reason", "Objek non-daun / perabot / pemandangan"),
            living_leaf_ratio,
            botanical_ratio,
        )

    largest_blob_ratio = morph_info.get("largest_blob_ratio", 0.0)
    living_blob_ratio = morph_info.get("living_blob_ratio", 0.0)
    is_soil_or_wood_dominated = (
        (necrotic_ratio >= 0.30 and living_leaf_ratio < 0.16)
        or ((necrotic_ratio + pitch_dark_ratio) >= 0.40 and living_leaf_ratio < 0.18)
    )

    if (
        botanical_ratio < 0.20
        or (living_leaf_ratio < 0.15 and necrotic_ratio < 0.15)
        or largest_blob_ratio < 0.18
        or is_soil_or_wood_dominated
        or (pitch_dark_ratio > 0.60 and living_leaf_ratio < 0.20)
    ):
        reasons_fail: list[str] = []
        if botanical_ratio < 0.20:
            reasons_fail.append(f"botanical={botanical_ratio*100:.1f}%<20%")
        if living_leaf_ratio < 0.15 and necrotic_ratio < 0.15:
            reasons_fail.append(f"living={living_leaf_ratio*100:.1f}% & necrotic={necrotic_ratio*100:.1f}%")
        if largest_blob_ratio < 0.18:
            reasons_fail.append(f"largest_blob={largest_blob_ratio*100:.1f}%<18%")
        if is_soil_or_wood_dominated:
            reasons_fail.append("dominasi tanah/kayu")
        if pitch_dark_ratio > 0.60:
            reasons_fail.append(f"pitch_dark={pitch_dark_ratio*100:.1f}%>60%")

        return _build_rejection_payload(
            "non_banana_leaf",
            f"Morfologi helai daun tidak memenuhi kriteria pisang: {', '.join(reasons_fail)}",
            living_leaf_ratio,
            botanical_ratio,
        )

    return {
        "valid": True,
        "rejection_type": None,
        "largest_blob_ratio": largest_blob_ratio,
        "living_blob_ratio": living_blob_ratio,
        "solidity": morph_info.get("solidity", 0.0),
        "significant_blobs_count": morph_info.get("num_blobs", 0),
        "true_green_ratio": true_green_ratio,
        "living_leaf_ratio": living_leaf_ratio,
        "botanical_ratio": botanical_ratio,
        "green_yellow_pct": round(living_leaf_ratio * 100, 2),
        "botanical_pct": round(botanical_ratio * 100, 2),
    }


def verify_yolo_boxes_against_raw_pixels(
    resized_bgr: np.ndarray,
    raw_boxes_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Filter YOLO predictions against pre-CLAHE raw pixels to reject false positives on skin, pots, or bare soil."""
    hsv_orig = cv2.cvtColor(resized_bgr, cv2.COLOR_BGR2HSV)
    ycrcb_orig = cv2.cvtColor(resized_bgr, cv2.COLOR_BGR2YCrCb)
    total_img_pixels = float(YOLO_IMAGE_SIZE * YOLO_IMAGE_SIZE)

    _, _, _, _, mask_whole = _compute_leaf_spectrum_masks(hsv_orig)
    mask_skin_orig = _compute_skin_mask(hsv_orig, ycrcb_orig)

    global_whole_ratio = np.count_nonzero(mask_whole) / total_img_pixels
    if global_whole_ratio < 0.20:
        return []

    verified: list[dict[str, Any]] = []
    for item in raw_boxes_data:
        x1, y1, x2, y2 = [int(v) for v in item["bbox"]]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(YOLO_IMAGE_SIZE, x2), min(YOLO_IMAGE_SIZE, y2)
        if x2 <= x1 + 5 or y2 <= y1 + 5:
            continue

        roi_hsv = hsv_orig[y1:y2, x1:x2]
        roi_pixels = float((x2 - x1) * (y2 - y1))

        ex1, ey1 = max(0, x1 - 25), max(0, y1 - 25)
        ex2, ey2 = min(YOLO_IMAGE_SIZE, x2 + 25), min(YOLO_IMAGE_SIZE, y2 + 25)
        exp_whole = mask_whole[ey1:ey2, ex1:ex2]
        exp_pixels = float((ex2 - ex1) * (ey2 - ey1))
        exp_whole_ratio = np.count_nonzero(exp_whole) / exp_pixels

        top_strip = mask_whole[max(0, y1 - 25) : y1, max(0, x1) : min(YOLO_IMAGE_SIZE, x2)]
        bot_strip = mask_whole[y2 : min(YOLO_IMAGE_SIZE, y2 + 25), max(0, x1) : min(YOLO_IMAGE_SIZE, x2)]
        left_strip = mask_whole[max(0, y1) : min(YOLO_IMAGE_SIZE, y2), max(0, x1 - 25) : x1]
        right_strip = mask_whole[max(0, y1) : min(YOLO_IMAGE_SIZE, y2), x2 : min(YOLO_IMAGE_SIZE, x2 + 25)]

        top_r = float(np.count_nonzero(top_strip)) / float(top_strip.size) if top_strip.size > 0 else 0.0
        bot_r = float(np.count_nonzero(bot_strip)) / float(bot_strip.size) if bot_strip.size > 0 else 0.0
        left_r = float(np.count_nonzero(left_strip)) / float(left_strip.size) if left_strip.size > 0 else 0.0
        right_r = float(np.count_nonzero(right_strip)) / float(right_strip.size) if right_strip.size > 0 else 0.0

        surrounding_whole_sides = sum(1 for r in [top_r, bot_r, left_r, right_r] if r >= 0.08)

        roi_green = np.count_nonzero(
            cv2.inRange(roi_hsv, np.array(HSV_GREEN_LOWER), np.array(HSV_GREEN_UPPER))
        ) / roi_pixels
        roi_yellow = np.count_nonzero(
            cv2.inRange(roi_hsv, np.array(HSV_YELLOW_LOWER), np.array(HSV_YELLOW_UPPER))
        ) / roi_pixels
        roi_living = roi_green + roi_yellow
        roi_skin = np.count_nonzero(mask_skin_orig[y1:y2, x1:x2]) / roi_pixels

        roi_necrotic = np.count_nonzero(
            cv2.inRange(roi_hsv, np.array(HSV_ROI_NECROTIC_LOWER), np.array(HSV_ROI_NECROTIC_UPPER))
        ) / roi_pixels
        roi_dark = np.count_nonzero(
            cv2.inRange(roi_hsv, np.array(HSV_ROI_DARK_LOWER), np.array(HSV_ROI_DARK_UPPER))
        ) / roi_pixels
        roi_pale_dry = np.count_nonzero(
            cv2.inRange(roi_hsv, np.array(HSV_PALE_DRY_LOWER), np.array(HSV_PALE_DRY_UPPER))
        ) / roi_pixels

        cls_name = item["class_name"]
        is_dry_lesion = roi_pale_dry >= 0.18 or roi_necrotic >= 0.15 or (roi_yellow + roi_dark) >= 0.20

        if cls_name in ["Black Sigatoka", "Cordana", "Pestalotiopsis", "Yellow Sigatoka"]:
            if roi_skin >= 0.20 and roi_green < 0.15:
                continue

            if (not is_dry_lesion) and roi_green < 0.15 and bot_r < 0.08 and (left_r < 0.08 or right_r < 0.08):
                continue

            if y2 >= int(0.85 * YOLO_IMAGE_SIZE) and roi_green < 0.03:
                roi_gray = cv2.cvtColor(resized_bgr[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
                roi_lap_var = float(cv2.Laplacian(roi_gray, cv2.CV_64F).var())
                roi_hues = roi_hsv[:, :, 0].flatten()
                roi_hue_std = float(np.std(roi_hues)) if len(roi_hues) > 0 else 0.0
                if roi_hue_std < 12.0 or roi_lap_var < 35.0:
                    continue

            if roi_green >= 0.75 and (roi_necrotic + roi_dark + roi_pale_dry) < 0.05 and roi_yellow < 0.15:
                continue

            if not is_dry_lesion:
                if roi_living < 0.05 and exp_whole_ratio < 0.20 and surrounding_whole_sides < 2:
                    continue
                if (roi_necrotic + roi_dark) >= 0.65 and exp_whole_ratio < 0.25 and surrounding_whole_sides < 2:
                    continue

            if global_whole_ratio < 0.30 and surrounding_whole_sides < 2 and not is_dry_lesion:
                if exp_whole_ratio < 0.25 or item["confidence_pct"] < 50.0:
                    continue

        elif cls_name == "Fresh":
            if (
                item["confidence_pct"] < 55.0
                or item["box_area_ratio_pct"] < 25.0
                or roi_green < 0.45
            ):
                continue

        verified.append(item)

    return verified
