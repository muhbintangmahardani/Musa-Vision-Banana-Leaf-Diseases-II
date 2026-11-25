import io
import os
import time
import base64
import cv2
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory
from ultralytics import YOLO
from PIL import Image, ExifTags, ImageOps

# Opsional: Torchvision MobileNetV3 (ImageNet 1000 kelas) untuk deteksi semantik objek non-daun & tanaman lain
try:
    import torch
    from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights
    IMAGENET_WEIGHTS = MobileNet_V3_Small_Weights.DEFAULT
    IMAGENET_MODEL = mobilenet_v3_small(weights=IMAGENET_WEIGHTS).eval()
    IMAGENET_PREPROCESS = IMAGENET_WEIGHTS.transforms()
    IMAGENET_CATEGORIES = IMAGENET_WEIGHTS.meta["categories"]
    HAS_IMAGENET_GUARD = True
except Exception as e:
    HAS_IMAGENET_GUARD = False
    print(f"[INFO] ImageNet Guard tidak aktif ({e}), menggunakan OpenCV Gatekeeper.")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Maksimal upload 16 MB

# ==============================================================================
# 1. PEMUATAN MODEL YOLO26 NANO (DARI OUTPUT KAGGLE)
# ==============================================================================
MODEL_PATHS = [
    os.path.join("models", "best_yolo26n_clahe.pt"),
    "best_yolo26n_clahe.pt",
    os.path.join("models", "best.pt"),
    "best.pt",
    os.path.join("models", "yolo26n.pt")
]

model = None
loaded_model_path = None
for path in MODEL_PATHS:
    if os.path.exists(path):
        model = YOLO(path)
        loaded_model_path = path
        print(f"[INFO] Model penyakit daun berhasil dimuat dari: {path}")
        break

if model is None:
    print("[WARNING] File 'models/best_yolo26n_clahe.pt' belum ditemukan!")

# Load OpenCV Haar Cascades (Deteksi Wajah Manusia / Selfie)
FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
FACE_ALT_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml"
)

# Detektor Siluet Tubuh Manusia Bawaan OpenCV (berjalan ringan tanpa file XML & tanpa Torchvision)
HOG_PEOPLE_DETECTOR = cv2.HOGDescriptor()
HOG_PEOPLE_DETECTOR.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Kata kunci kelas ImageNet untuk OBJEK NON-DAUN (Manusia, Pakaian, Pemandangan, Tanah, Hewan, Barang)
REJECTED_NON_LEAF_KEYWORDS = [
    "fish", "tench", "shark", "ray", "stingray", "eel", "coho", "salmon", "trout",
    "barracuda", "sturgeon", "gar", "puffer", "crab", "lobster", "crayfish", "shrimp",
    "whale", "dolphin", "seal", "jellyfish", "squid", "octopus", "shell", "snail",
    "plate", "platter", "burrito", "tamale", "meat loaf", "potpie", "pizza", "sandwich",
    "hotdog", "hamburger", "soup", "bowl", "tray", "frying pan", "wok", "skillet",
    "grill", "rotisserie", "bakery", "dough", "menu", "dining table", "restaurant",
    "ice cream", "chocolate", "cake", "pie", "bread", "bagel", "pretzel",
    "guacamole", "consomme", "hot pot", "trifle", "carbonara", "spaghetti",
    "person", "groom", "scuba diver", "player", "ballplayer", "sunglass", "glasses", "wig",
    "mask", "shirt", "jersey", "t-shirt", "sweatshirt", "suit", "coat", "jacket", "tie",
    "hat", "cap", "helmet", "shoe", "sandal", "jean", "denim", "cardigan", "cloak",
    "vest", "pajama", "poncho", "trench coat", "brassiere", "swimming trunks", "swimming",
    "bikini", "maillot", "military uniform", "abaya", "miniskirt", "overskirt", "hoopskirt",
    "shorts", "trouser", "pant", "kimono", "sarong", "stole", "fur coat", "lab coat",
    "bulletproof vest", "apron", "bib", "sombrero", "bonnet", "beret", "cowboy hat",
    "mortarboard", "academic gown", "bolo tie", "bow tie", "sock", "mitten", "glove",
    "boot", "sneaker", "running shoe", "clog", "loafer", "backpack", "purse", "wallet",
    "umbrella", "hair spray", "lipstick",
    "dog", "cat", "bird", "hen", "cock", "chicken", "duck", "goose", "monkey", "horse",
    "cow", "ox", "pig", "hog", "sheep", "goat", "elephant", "bear", "tiger", "lion",
    "snake", "lizard", "frog", "toad", "turtle", "rabbit", "mouse", "rat",
    "laptop", "notebook", "computer", "monitor", "television", "cellular",
    "phone", "keyboard", "remote", "camera", "chair", "couch", "sofa", "bed",
    "desk", "wardrobe", "bookcase", "car", "bus", "truck", "motorcycle", "bicycle",
    "bottle", "cup", "mug",
    # Danau / Air / Pantai / Kapal / Dermaga (Lake, Water, Shore, Boat, Pier)
    "lakeside", "seashore", "promontory", "sandbar", "breakwater", "pier", "dock", "dam",
    "canoe", "paddle", "gondola", "speedboat", "lifeboat", "airship", "boathouse",
    "beacon", "lighthouse", "fountain", "geyser", "water bottle", "water jug", "water tower",
    # Lanskap / Pemandangan / Tanah / Bebatuan / Kayu Pohon
    "valley", "cliff", "alp", "volcano", "mountain tent", "mountain bike",
    "stone wall", "megalith", "quarry", "dirt", "soil", "earth", "gravel", "sand", "mud",
    "park bench", "street", "road", "highway", "bridge", "building", "house", "barn",
    "roof", "fence", "worm fence", "chainlink fence", "pole", "sign", "trash", "ashcan",
    "wooden spoon", "lumber", "log"
]

# Himpunan kategori ImageNet yang merupakan hasil prediksi wajar (false confusion) pada daun pisang
# karena kemiripan tekstur mikro garis sejajar, klorofil hijau pekat, atau bercak jamur:
LEAF_CONFUSION_CATEGORIES = {
    "tree frog", "bullfrog", "tailed frog", "leafhopper", "vine snake", "quill", "sea anemone",
    "shower curtain", "theater curtain", "mosquito net", "velvet", "window shade",
    "jigsaw puzzle", "coral fungus", "agaric", "bolete", "banana", "ear", "corn",
    "zucchini", "cucumber", "head cabbage", "artichoke", "broccoli", "rapeseed",
    "green lizard", "sulphur butterfly", "American chameleon", "flatworm", "mud turtle",
    "box turtle", "terrapin", "agama", "alligator lizard", "garter snake", "water snake",
    "grasshopper", "mantis", "cicada", "tray", "spaghetti squash", "butternut squash",
    "acorn squash", "hen-of-the-woods"
}

# Kata kunci kelas ImageNet untuk POT BUNGA, PERABOT RUANGAN & TANAMAN HIAS
POT_AND_OTHER_PLANT_KEYWORDS = [
    "pot", "flowerpot", "vase", "planter", "greenhouse",
    "daisy", "rose", "sunflower", "tulip", "orchid", "lily", "hibiscus",
    "broccoli", "cauliflower", "head cabbage", "bell pepper", "cucumber",
    "zucchini", "strawberry", "pineapple", "pomegranate", "acorn", "maple", "oak",
    "picket fence", "patio", "window", "curtain", "table", "desk", "chair", "couch",
    "bucket", "basket", "barrel", "crate",
    "terracotta", "urn", "tub", "mortar", "ashcan", "trash", "potted", "porch",
    "tile", "floor", "wall", "brick", "ceramic", "clay", "plastic bag"
]

# Kata kunci tanda tangan Generator AI pada Nama File
AI_FILENAME_KEYWORDS = [
    "midjourney", "dall-e", "dalle", "stable diffusion", "stablediffusion",
    "sdxl", "comfyui", "automatic1111", "bing image creator", "firefly",
    "adobe firefly", "leonardo.ai", "ideogram", "novelai", "ai_generated", "ai-generated"
]

# Kata kunci tanda tangan Generator AI pada Metadata Biner (Chunks / Diffusion Tags)
AI_METADATA_KEYWORDS = [
    "trainedalgorithmicmedia", "digitalsourcetype/trainedalgorithmicmedia",
    "midjourney", "dall-e", "dalle", "stablediffusion", "stable diffusion", "comfyui",
    "automatic1111", "adobe firefly", "leonardo.ai", "ideogram", "novelai"
]

# Resolusi standar generator AI untuk pengecekan tekstur sintetis (tanpa EXIF kamera)
EXACT_AI_RESOLUTIONS = {
    (1024, 1024), (1024, 1792), (1792, 1024), (1024, 1536), (1536, 1024),
    (1344, 768), (768, 1344), (512, 512), (768, 768), (2048, 2048)
}

VALID_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}

# ==============================================================================
# 2. BASIS PENGETAHUAN AGRONOMI, SANITASI (DELEAFING), & KODE FRAC
# ==============================================================================
AGRONOMY_KB = {
    "Fresh": {
        "display_name": "Daun Sehat (Fresh)",
        "scientific_name": "Musa spp. (Helai Daun Fungsional Sehat)",
        "severity_category": "Sehat Optimal",
        "default_granularity": "Leaf-Level (Level Helai Daun)",
        "color_hex": "#16a34a",
        "bgr_color": (74, 163, 22),
        "symptoms": "Permukaan helai daun hijau segar merata tanpa goresan klorosis kuning maupun bercak kering nekrotik.",
        "deleafing_protocol": (
            "Tidak diperlukan pemangkasan sanitasi. Pertahankan minimal 6 hingga 8 helai daun "
            "fungsional yang sehat per pohon pada fase pembungaan hingga pengisian tandan buah."
        ),
        "frac_recommendation": "Tidak diperlukan penyemprotan fungisida.",
        "frac_codes": ["Tidak Diperlukan Fungisida"],
        "ppl_disclaimer": (
            "Tetap lakukan pemantauan rutin kebun setiap minggu dan jaga sanitasi drainase lahan."
        )
    },
    "Black Sigatoka": {
        "display_name": "Sigatoka Hitam (Black Sigatoka)",
        "scientific_name": "Pseudocercospora fijiensis",
        "severity_category": "Penyakit Jamur Ganas Utama (Risiko gagal panen hingga 50%)",
        "default_granularity": "Lesion-Level (Level Bercak)",
        "color_hex": "#dc2626",
        "bgr_color": (38, 38, 220),
        "symptoms": (
            "Bintik atau goresan tipis (streaks) cokelat kemerahan di bawah daun yang melebar "
            "menjadi bercak memanjang cokelat tua hingga hitam pekat dan membuat daun mengering cepat."
        ),
        "deleafing_protocol": (
            "Pangkas bagian helai daun yang sudah mengalami nekrosis hitam menggunakan pisau bersih (deleafing) "
            "dan kumpulkan di luar area tanam untuk memutus sebaran spora. Wajib menyisakan minimal 6-8 daun sehat per pohon."
        ),
        "frac_recommendation": (
            "Gunakan Fungisida Sistemik Kuratif golongan Triazol (Difenoconazole / Tebuconazole — [Kode FRAC 3]) "
            "yang dirotasi dengan golongan Strobilurin (Azoxystrobin — [Kode FRAC 11]) untuk menghentikan "
            "pertumbuhan jamur di dalam jaringan daun."
        ),
        "frac_codes": ["FRAC 3 (Triazol: Difenoconazole/Tebuconazole)", "FRAC 11 (Strobilurin: Azoxystrobin)"],
        "ppl_disclaimer": (
            "PERINGATAN PPL/POPT: Wajib melakukan rotasi bahan aktif antar-kode FRAC agar jamur tidak kebal (resisten). "
            "Konsultasikan dosis penyemprotan dengan Penyuluh Pertanian Lapangan (PPL) atau petugas POPT setempat."
        )
    },
    "Yellow Sigatoka": {
        "display_name": "Sigatoka Kuning (Yellow Sigatoka)",
        "scientific_name": "Pseudocercospora musae",
        "severity_category": "Penyakit Jamur Ganas Utama",
        "default_granularity": "Leaf-Level (Level Helai Daun)",
        "color_hex": "#eab308",
        "bgr_color": (8, 179, 234),
        "symptoms": (
            "Garis-garis pucat kekuningan (yellow streaks) sejajar tulang daun di tepi helai daun yang "
            "berubah menjadi bercak lonjong cokelat dengan bagian tengah abu-abu kering dan batas kuning jelas."
        ),
        "deleafing_protocol": (
            "Pangkas bagian tepi atau lembaran daun yang sudah menguning dan mengering parah menggunakan pisau sanitasi bersih, "
            "dengan tetap mempertahankan minimal 6-8 helai daun fungsional per pohon."
        ),
        "frac_recommendation": (
            "Gunakan Fungisida Sistemik Kuratif [Kode FRAC 3] (Difenoconazole / Tebuconazole) atau [Kode FRAC 11] (Azoxystrobin) "
            "secara bergilir, serta dapat dikombinasikan dengan fungisida kontak protektif [Kode FRAC M03/M05] pada gejala awal."
        ),
        "frac_codes": ["FRAC 3 (Triazol)", "FRAC 11 (Strobilurin)", "FRAC M03/M05 (Kontak Protektif)"],
        "ppl_disclaimer": (
            "PERINGATAN PPL/POPT: Jangan menyemprotkan satu kode FRAC sistemik secara terus-menerus. "
            "Koordinasikan jadwal penyemprotan dengan PPL atau petugas POPT setempat."
        )
    },
    "Cordana": {
        "display_name": "Bercak Daun Cordana (Cordana Leaf Spot)",
        "scientific_name": "Cordana musae",
        "severity_category": "Penyakit Jamur Sekunder (Kategori Ringan - Sedang)",
        "default_granularity": "Lesion-Level (Level Bercak)",
        "color_hex": "#f97316",
        "bgr_color": (22, 115, 249),
        "symptoms": (
            "Bercak berbentuk oval besar menyerupai mata berlian (diamond-shaped) berwarna cokelat pucat "
            "dengan pola lingkaran berlapis (zonate) dan dikelilingi cincin kuning terang (bright yellow halo)."
        ),
        "deleafing_protocol": (
            "Pangkas bagian tepi daun yang terinfeksi bercak oval kering agar tidak meluas, "
            "tanpa memangkas habis seluruh pelepah daun sehat."
        ),
        "frac_recommendation": (
            "Cukup gunakan Fungisida Kontak Protektif yang ekonomis seperti Mancozeb [Kode FRAC M03] "
            "atau Chlorothalonil [Kode FRAC M05]. Tidak memerlukan fungisida sistemik mahal."
        ),
        "frac_codes": ["FRAC M03 (Mancozeb)", "FRAC M05 (Chlorothalonil)"],
        "ppl_disclaimer": (
            "Catatan PPL: Infeksi Cordana bersifat sekunder. Hindari pemborosan biaya dengan tidak membeli "
            "fungisida sistemik dosis tinggi kecuali ditemukan infeksi ganda dengan Sigatoka."
        )
    },
    "Pestalotiopsis": {
        "display_name": "Bercak Daun Pestalotiopsis",
        "scientific_name": "Pestalotiopsis microspora / leprogena",
        "severity_category": "Penyakit Jamur Sekunder (Kategori Ringan - Sedang)",
        "default_granularity": "Lesion-Level (Level Bercak)",
        "color_hex": "#8b5cf6",
        "bgr_color": (246, 92, 139),
        "symptoms": (
            "Bintik-bintik bercak kecil tidak beraturan (ireguler) berwarna cokelat keabu-abuan dengan tepian "
            "cokelat gelap di pinggir atau ujung daun yang sering robek akibat gesekan angin."
        ),
        "deleafing_protocol": (
            "Bersihkan ujung atau pinggiran helai daun yang robek dan mengering untuk mengurangi sumber spora."
        ),
        "frac_recommendation": (
            "Gunakan Fungisida Kontak Protektif berbahan aktif Mancozeb [Kode FRAC M03] atau "
            "Chlorothalonil [Kode FRAC M05] apabila bercak mulai meluas di musim hujan."
        ),
        "frac_codes": ["FRAC M03 (Mancozeb)", "FRAC M05 (Chlorothalonil)"],
        "ppl_disclaimer": (
            "Catatan PPL: Jamur ini umumnya masuk melalui luka gesekan mekanis/angin. "
            "Konsultasikan ke PPL setempat jika gejala menyebar ke daun muda."
        )
    }
}


def normalize_class_name(raw_name: str) -> str:
    cleaned = raw_name.strip().lower().replace("_", " ").replace("-", " ")
    if "black" in cleaned:
        return "Black Sigatoka"
    if "yellow" in cleaned:
        return "Yellow Sigatoka"
    if "cordana" in cleaned:
        return "Cordana"
    if "pestalotiopsis" in cleaned or "pestalotia" in cleaned:
        return "Pestalotiopsis"
    if "fresh" in cleaned or "healthy" in cleaned or "sehat" in cleaned:
        return "Fresh"
    return "Fresh"


# ==============================================================================
# 3. DETEKTOR CITRA GENERATE AI (METADATA C2PA/EXIF + TEKSTUR LAPLACIAN/SMOOTHNESS)
# ==============================================================================
def detect_ai_generated_image(file_bytes: bytes, filename: str, img_bgr: np.ndarray) -> dict:
    """
    Mendeteksi apakah gambar merupakan hasil generate AI melalui:
    1. Pemeriksaan nama file eksplisit AI generator.
    2. Pemeriksaan metadata biner (C2PA / XMP / PNG parameters / EXIF Software).
    3. Analisis tekstur plastis/airbrushed via varians Laplacian & smoothness
       (hanya pada resolusi kanvas baku AI tanpa EXIF kamera).
    """
    fname_lower = (filename or "").lower()
    for kw in AI_FILENAME_KEYWORDS:
        if kw in fname_lower:
            return {
                "is_ai": True,
                "reason": (
                    f"Terdeteksi Gambar Hasil Generate AI (Jejak nama file: '{kw}'). "
                    "Sistem MusaVision hanya memproses foto daun pisang asli dari kebun/kamera, "
                    "bukan citra sintetis buatan AI."
                )
            }

    # Cek string biner C2PA / Content Credentials / chunk generator AI
    binary_sample = file_bytes[:131072] + (file_bytes[-65536:] if len(file_bytes) > 65536 else b"")
    raw_latin = binary_sample.decode("latin-1", errors="ignore").lower()
    for kw in AI_METADATA_KEYWORDS:
        if kw in raw_latin:
            return {
                "is_ai": True,
                "reason": (
                    f"Terdeteksi Gambar Hasil Generate AI (Metadata C2PA/XMP/Software mengandung '{kw}'). "
                    "Citra sintetis buatan AI memiliki pola pencahayaan buatan yang tidak valid untuk diagnosis penyakit."
                )
            }

    # Cek Metadata Pillow Info (tEXt chunks, prompt, parameters, workflow) & EXIF Kamera Asli
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
                        "reason": f"Terdeteksi Gambar Hasil Generate AI pada metadata teks PNG ({k})."
                    }
                if k_lower in ["parameters", "prompt", "workflow"]:
                    if any(
                        term in v_lower
                        for term in [
                            "steps:", "sampler:", "cfg scale:", "seed:",
                            "ksampler", "checkpointloader", "--ar", "--v 5", "--v 6"
                        ]
                    ):
                        return {
                            "is_ai": True,
                            "reason": f"Terdeteksi Gambar Hasil Generate AI pada metadata alur kerja difusi ({k})."
                        }

        exif_dict = {}
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
                    "reason": f"Terdeteksi Gambar Hasil Generate AI pada atribut EXIF Software ('{val_str}')."
                }
            if tag_name in ["make", "model", "lensmodel", "focallength", "isospeedratings", "datetimeoriginal"]:
                if len(val_str.strip()) > 1:
                    has_camera_exif = True
    except Exception:
        pass

    if has_camera_exif:
        return {"is_ai": False, "reason": "Memiliki EXIF kamera asli."}

    h, w = img_bgr.shape[:2]
    is_dataset_size = (w == 640 and h == 640)

    if (w, h) in EXACT_AI_RESOLUTIONS and not is_dataset_size:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32)
        lap_var = float(np.var(cv2.Laplacian(gray, cv2.CV_32F)))
        blur_diff = np.abs(gray - cv2.GaussianBlur(gray, (5, 5), 0))
        hyper_smooth_ratio = float(np.mean(blur_diff < 1.8))

        if hyper_smooth_ratio > 0.96 and lap_var < 15.0:
            return {
                "is_ai": True,
                "reason": (
                    f"Terdeteksi Gambar Hasil Generate AI (Resolusi sintetis {w}×{h} tanpa EXIF kamera "
                    "dengan tekstur permukaan plastis/airbrushed tanpa serat urat daun alami)."
                )
            }

    return {"is_ai": False, "reason": "Bukan citra AI."}


STANDARD_NON_BANANA_TITLE = "Objek Bukan Daun Pisang"
STANDARD_NON_BANANA_REASON = (
    "Citra yang diunggah teridentifikasi sebagai objek bukan daun pisang. "
    "Mohon fokuskan kamera pada permukaan helai daun pisang (Musa spp.) tanpa menyertakan pot, manusia, atau objek lain."
)

POT_SENSITIVE_KEYWORDS = {
    "pot", "flowerpot", "vase", "planter", "greenhouse", "houseplant", "bonsai",
    "daisy", "rose", "sunflower", "tulip", "orchid", "lily", "hibiscus", "earthstar",
    "terracotta", "urn", "tub", "mortar", "potted", "ashcan", "trash", "bucket",
    "basket", "barrel", "crate", "table", "desk", "chair", "couch", "ceramic", "clay"
}


# ==============================================================================
# 4. ANALISIS MORFOLOGI & GUARD SEMANTIK DAUN PISANG VS OBJEK/PEMANDANGAN/TANAMAN LAIN
# ==============================================================================
def analyze_banana_vs_other_leaf(
    img_bgr: np.ndarray,
    mask_whole_leaf: np.ndarray,
    mask_leaf_lamina: np.ndarray
) -> dict:
    h, w = img_bgr.shape[:2]
    total_pixels = float(h * w)
    living_leaf_ratio = np.count_nonzero(mask_leaf_lamina) / total_pixels

    # 1. Cek semantik via MobileNetV3 (Top-10 untuk non-daun/pemandangan & pot/tanaman lain)
    if HAS_IMAGENET_GUARD:
        try:
            rgb_pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
            input_tensor = IMAGENET_PREPROCESS(rgb_pil).unsqueeze(0)
            with torch.no_grad():
                logits = IMAGENET_MODEL(input_tensor)
                probs = torch.nn.functional.softmax(logits[0], dim=0)
                top10_prob, top10_catid = torch.topk(probs, 10)

            non_leaf_score_sum = 0.0
            matched_non_leaf_names = []
            for i in range(10):
                cat_name = IMAGENET_CATEGORIES[top10_catid[i]].lower()
                prob_val = float(top10_prob[i].item())
                if (
                    any(kw in cat_name for kw in REJECTED_NON_LEAF_KEYWORDS)
                    and cat_name not in LEAF_CONFUSION_CATEGORIES
                ):
                    non_leaf_score_sum += prob_val
                    matched_non_leaf_names.append(f"{cat_name} {prob_val*100:.1f}%")
                    # Jika citra memiliki proporsi daun hidup rendah (< 65%), tolak dengan ambang sensitif 0.05 (5%)
                    # Jika citra memiliki daun hidup dominan (>= 65%), hanya tolak jika probabilitas >= 0.22
                    is_clear_non_leaf = (
                        (living_leaf_ratio < 0.65 and prob_val >= 0.05)
                        or (prob_val >= 0.22)
                    )
                    if is_clear_non_leaf:
                        return {
                            "is_non_leaf_object": True,
                            "title": STANDARD_NON_BANANA_TITLE,
                            "reason": STANDARD_NON_BANANA_REASON,
                            "internal_reason": f"ImageNet semantik non-daun: {cat_name} ({prob_val*100:.1f}%)",
                            "largest_blob_ratio": 0.0,
                            "living_blob_ratio": 0.0,
                            "solidity": 0.0,
                            "num_blobs": 0
                        }

            if (living_leaf_ratio < 0.65 and non_leaf_score_sum >= 0.10) or (living_leaf_ratio >= 0.65 and non_leaf_score_sum >= 0.50):
                return {
                    "is_non_leaf_object": True,
                    "title": STANDARD_NON_BANANA_TITLE,
                    "reason": STANDARD_NON_BANANA_REASON,
                    "internal_reason": f"ImageNet skor non-daun kumulatif tinggi ({non_leaf_score_sum*100:.1f}%): {', '.join(matched_non_leaf_names)}",
                    "largest_blob_ratio": 0.0,
                    "living_blob_ratio": 0.0,
                    "solidity": 0.0,
                    "num_blobs": 0
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
                            "num_blobs": 0
                        }
        except Exception:
            pass

    # 2. Hitung Kontur Daun Utuh & Kontur Daun Hidup (Hijau + Kuning TANPA warna tanah/cokelat)
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
            "num_blobs": 0
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
        "num_blobs": len(significant_blobs)
    }


# ==============================================================================
# 5. GATEKEEPER UTAMA (PRA-YOLO)
# ==============================================================================
def validate_image_gatekeeper(img_bgr: np.ndarray, file_bytes: bytes, filename: str) -> dict:
    """
    Urutan Validasi Gatekeeper:
    1. Cek Gambar Hasil Generate AI (AI-Generated Image).
    2. Cek Daun Sintetis / Plastik.
    3. Cek Wajah Manusia, Siluet Tubuh Manusia (HOG), & Warna Kulit.
    4. Cek Objek Pot / Pemandangan / Tanaman Lain via MobileNetV3 & morfologi lamina hidup.
    5. Cek Spektrum Klorofil, Dominasi Tanah, & Lamina Hidup Menyatu.
    """
    h, w = img_bgr.shape[:2]
    total_pixels = float(h * w)

    # --- TAHAP 1: DETEKSI GAMBAR HASIL GENERATE AI ---
    ai_check = detect_ai_generated_image(file_bytes, filename, img_bgr)
    if ai_check["is_ai"]:
        return {
            "valid": False,
            "rejection_type": "ai_generated",
            "title": STANDARD_NON_BANANA_TITLE,
            "reason": STANDARD_NON_BANANA_REASON,
            "internal_reason": f"AI-Generated Image: {ai_check['reason']}",
            "green_yellow_pct": 0.0,
            "botanical_pct": 0.0
        }

    # Hitung spektrum warna di ruang HSV & YCrCb
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    ycrcb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2YCrCb)
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Masker Kulit Manusia
    mask_skin_ycrcb = cv2.inRange(ycrcb, np.array([60, 133, 80]), np.array([255, 175, 130]))
    mask_skin_hsv = cv2.inRange(hsv, np.array([0, 25, 50]), np.array([24, 200, 255]))
    mask_skin = cv2.bitwise_and(mask_skin_ycrcb, mask_skin_hsv)
    skin_ratio = np.count_nonzero(mask_skin) / total_pixels

    # Masker Hijau Klorofil (Hue: 32 - 92, Sat >= 30, Val >= 28)
    mask_true_green = cv2.inRange(hsv, np.array([32, 30, 28]), np.array([92, 255, 255]))
    true_green_ratio = np.count_nonzero(mask_true_green) / total_pixels

    # Masker Kuning Klorosis Daun Pisang (Hue: 18 - 32, Sat >= 40, Val >= 45)
    mask_yellow = cv2.inRange(hsv, np.array([18, 40, 45]), np.array([32, 255, 255]))
    yellow_ratio = np.count_nonzero(mask_yellow) / total_pixels

    # Masker Cokelat Nekrotik / Tanah (Hue: 4 - 22, Sat >= 25, Val: 20 - 195)
    mask_necrotic = cv2.inRange(hsv, np.array([4, 25, 20]), np.array([22, 255, 195]))
    necrotic_ratio = np.count_nonzero(mask_necrotic) / total_pixels

    # Masker Lamina Daun Hidup (Hijau + Kuning) & Helai Daun Utuh (+ Nekrotik)
    mask_leaf_lamina = cv2.bitwise_or(mask_true_green, mask_yellow)
    mask_whole_leaf = cv2.bitwise_or(mask_leaf_lamina, mask_necrotic)
    living_leaf_ratio = true_green_ratio + yellow_ratio
    botanical_ratio = np.count_nonzero(mask_whole_leaf) / total_pixels

    # Masker Gelap Pekat Hitam/Abu-abu (Val < 42)
    mask_pitch_dark = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 42]))
    pitch_dark_ratio = np.count_nonzero(mask_pitch_dark) / total_pixels

    # Masker pantulan spekular khas plastik buatan
    mask_specular = cv2.inRange(hsv, np.array([0, 0, 220]), np.array([180, 30, 255]))
    specular_ratio = np.count_nonzero(mask_specular) / total_pixels

    # --- TAHAP 1B: DETEKSI DAUN SINTETIS / PLASTIK ---
    green_pixels = np.count_nonzero(mask_true_green)
    if green_pixels > 500:
        hue_vals = hsv[mask_true_green > 0, 0]
        hue_std = float(np.std(hue_vals))
        sat_vals = hsv[mask_true_green > 0, 1]
        sat_std = float(np.std(sat_vals))
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

        is_synthetic = (
            (specular_ratio >= 0.05 and hue_std < 4.0 and lap_var < 35.0) or
            (hue_std < 1.8 and sat_std < 15.0 and true_green_ratio >= 0.20)
        )
        if is_synthetic:
            return {
                "valid": False,
                "rejection_type": "non_banana_leaf",
                "title": STANDARD_NON_BANANA_TITLE,
                "reason": STANDARD_NON_BANANA_REASON,
                "internal_reason": "Daun sintetis / plastik (lap_var rendah & spekular tinggi)",
                "green_yellow_pct": round(living_leaf_ratio * 100, 2),
                "botanical_pct": round(botanical_ratio * 100, 2)
            }

    # --- TAHAP 2: BLOKIR WAJAH, TUBUH MANUSIA (HOG), KULIT, & PEMANDANGAN LUAR ---
    min_face = (max(20, int(min(w, h) * 0.04)), max(20, int(min(w, h) * 0.04)))
    detected_faces = (
        list(FACE_CASCADE.detectMultiScale(gray, 1.1, 4, minSize=min_face)) +
        list(FACE_ALT_CASCADE.detectMultiScale(gray, 1.1, 4, minSize=min_face))
    )
    verified_faces = []
    for (fx, fy, fw, fh) in detected_faces:
        roi_ycrcb = ycrcb[fy:fy+fh, fx:fx+fw]
        roi_hsv = hsv[fy:fy+fh, fx:fx+fw]
        m_s = cv2.bitwise_and(
            cv2.inRange(roi_ycrcb, np.array([60, 133, 80]), np.array([255, 175, 130])),
            cv2.inRange(roi_hsv, np.array([0, 25, 50]), np.array([24, 200, 255]))
        )
        m_g = cv2.inRange(roi_hsv, np.array([32, 30, 28]), np.array([92, 255, 255]))
        face_skin_r = np.count_nonzero(m_s) / float(fw * fh)
        face_green_r = np.count_nonzero(m_g) / float(fw * fh)
        if face_skin_r >= 0.20 and face_green_r < 0.35:
            verified_faces.append((fx, fy, fw, fh))

    if len(verified_faces) > 0 and living_leaf_ratio < 0.70:
        return {
            "valid": False,
            "rejection_type": "non_banana_leaf",
            "title": STANDARD_NON_BANANA_TITLE,
            "reason": STANDARD_NON_BANANA_REASON,
            "internal_reason": f"Terdeteksi wajah manusia ({len(verified_faces)} wajah terverifikasi)",
            "green_yellow_pct": round(living_leaf_ratio * 100, 2),
            "botanical_pct": round(botanical_ratio * 100, 2)
        }

    # Deteksi siluet tubuh manusia berdiri/jarak jauh via OpenCV HOG (termasuk membelakangi kamera)
    if living_leaf_ratio < 0.55:
        scale_w = max(128, min(480, w))
        scale_h = max(160, int(h * (scale_w / float(w))))
        small_bgr = cv2.resize(img_bgr, (scale_w, scale_h))
        _, weights = HOG_PEOPLE_DETECTOR.detectMultiScale(
            small_bgr, winStride=(8, 8), padding=(8, 8), scale=1.05
        )
        strong_people = [float(wt) for wt in np.ravel(weights) if float(wt) >= 0.45] if len(weights) > 0 else []
        if len(strong_people) > 0:
            return {
                "valid": False,
                "rejection_type": "non_banana_leaf",
                "title": STANDARD_NON_BANANA_TITLE,
                "reason": STANDARD_NON_BANANA_REASON,
                "internal_reason": f"Siluet tubuh manusia terdeteksi (HOG weights={strong_people})",
                "green_yellow_pct": round(living_leaf_ratio * 100, 2),
                "botanical_pct": round(botanical_ratio * 100, 2)
            }

    # Kulit manusia (selfie dekat, tangan, lengan, orang di luar ruangan)
    if (skin_ratio >= 0.15 and living_leaf_ratio < 0.40) or (skin_ratio >= 0.08 and living_leaf_ratio < 0.25):
        return {
            "valid": False,
            "rejection_type": "non_banana_leaf",
            "title": STANDARD_NON_BANANA_TITLE,
            "reason": STANDARD_NON_BANANA_REASON,
            "internal_reason": f"Dominasi warna kulit manusia ({skin_ratio*100:.1f}%)",
            "green_yellow_pct": round(living_leaf_ratio * 100, 2),
            "botanical_pct": round(botanical_ratio * 100, 2)
        }

    # Deteksi air danau / langit terbuka di pemandangan luar ruangan
    mask_water_blue = cv2.inRange(hsv, np.array([92, 30, 40]), np.array([135, 255, 255]))
    water_blue_ratio = np.count_nonzero(mask_water_blue) / total_pixels
    if water_blue_ratio >= 0.035 and living_leaf_ratio < 0.65:
        return {
            "valid": False,
            "rejection_type": "non_banana_leaf",
            "title": STANDARD_NON_BANANA_TITLE,
            "reason": STANDARD_NON_BANANA_REASON,
            "internal_reason": f"Unsur air/langit terbuka di pemandangan ({water_blue_ratio*100:.1f}%)",
            "green_yellow_pct": round(living_leaf_ratio * 100, 2),
            "botanical_pct": round(botanical_ratio * 100, 2)
        }

    # Analisis Morfologi Daun Pisang vs Objek / Pemandangan / Tanaman Lain
    morph_info = analyze_banana_vs_other_leaf(img_bgr, mask_whole_leaf, mask_leaf_lamina)

    if morph_info.get("is_other_leaf"):
        return {
            "valid": False,
            "rejection_type": "non_banana_leaf",
            "title": STANDARD_NON_BANANA_TITLE,
            "reason": STANDARD_NON_BANANA_REASON,
            "internal_reason": morph_info.get("internal_reason", "Morfologi tanaman lain / wadah pot"),
            "green_yellow_pct": round(living_leaf_ratio * 100, 2),
            "botanical_pct": round(botanical_ratio * 100, 2)
        }

    if morph_info.get("is_non_leaf_object"):
        return {
            "valid": False,
            "rejection_type": "non_banana_leaf",
            "title": STANDARD_NON_BANANA_TITLE,
            "reason": STANDARD_NON_BANANA_REASON,
            "internal_reason": morph_info.get("internal_reason", "Objek non-daun / perabot / pemandangan"),
            "green_yellow_pct": round(living_leaf_ratio * 100, 2),
            "botanical_pct": round(botanical_ratio * 100, 2)
        }

    # Aturan Lolos Daun Pisang vs Tolak Foto Tanah / Kayu Pohon / Pemandangan
    largest_blob_ratio = morph_info.get("largest_blob_ratio", 0.0)
    living_blob_ratio = morph_info.get("living_blob_ratio", 0.0)
    is_soil_or_wood_dominated = (
        (necrotic_ratio >= 0.30 and living_leaf_ratio < 0.16) or
        ((necrotic_ratio + pitch_dark_ratio) >= 0.40 and living_leaf_ratio < 0.18)
    )

    if (
        botanical_ratio < 0.20
        or (living_leaf_ratio < 0.15 and necrotic_ratio < 0.15)
        or largest_blob_ratio < 0.18
        or is_soil_or_wood_dominated
        or (pitch_dark_ratio > 0.60 and living_leaf_ratio < 0.20)
    ):
        reasons_fail = []
        if botanical_ratio < 0.20: reasons_fail.append(f"botanical={botanical_ratio*100:.1f}%<20%")
        if (living_leaf_ratio < 0.15 and necrotic_ratio < 0.15): reasons_fail.append(f"living={living_leaf_ratio*100:.1f}% & necrotic={necrotic_ratio*100:.1f}%")
        if largest_blob_ratio < 0.18: reasons_fail.append(f"largest_blob={largest_blob_ratio*100:.1f}%<18%")
        if is_soil_or_wood_dominated: reasons_fail.append("dominasi tanah/kayu")
        if pitch_dark_ratio > 0.60: reasons_fail.append(f"pitch_dark={pitch_dark_ratio*100:.1f}%>60%")

        return {
            "valid": False,
            "rejection_type": "non_banana_leaf",
            "title": STANDARD_NON_BANANA_TITLE,
            "reason": STANDARD_NON_BANANA_REASON,
            "internal_reason": f"Morfologi helai daun tidak memenuhi kriteria pisang: {', '.join(reasons_fail)}",
            "green_yellow_pct": round(living_leaf_ratio * 100, 2),
            "botanical_pct": round(botanical_ratio * 100, 2)
        }

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
        "botanical_pct": round(botanical_ratio * 100, 2)
    }


# ==============================================================================
# 6. VERIFIKASI PASCA-YOLO (ATURAN BIOLOGIS ANTI TANAH, KULIT, POT, & DAUN LAIN)
# ==============================================================================
def verify_yolo_boxes_against_raw_pixels(resized_bgr: np.ndarray, raw_boxes_data: list) -> list:
    """
    Memverifikasi kotak prediksi YOLO terhadap piksel asli pra-CLAHE:
    - Meloloskan kotak bercak penyakit asli (termasuk bercak abu-abu pucat Pestalotiopsis & Cordana).
    - Membuang kotak palsu pada kulit manusia, tanah, pot bunga, atau objek gelap terpisah dari daun.
    - Mencegah daun hijau sehat pada pot tanaman berubah menjadi bercak Black Sigatoka.
    - Memperketat kelas 'Fresh' agar daun tanaman lain tidak mudah dianggap Fresh.
    """
    hsv_orig = cv2.cvtColor(resized_bgr, cv2.COLOR_BGR2HSV)
    ycrcb_orig = cv2.cvtColor(resized_bgr, cv2.COLOR_BGR2YCrCb)
    total_img_pixels = 640.0 * 640.0

    mask_green = cv2.inRange(hsv_orig, np.array([32, 30, 28]), np.array([92, 255, 255]))
    mask_yellow = cv2.inRange(hsv_orig, np.array([18, 40, 45]), np.array([32, 255, 255]))
    mask_necrotic = cv2.inRange(hsv_orig, np.array([4, 25, 20]), np.array([22, 255, 195]))
    mask_living = cv2.bitwise_or(mask_green, mask_yellow)
    mask_whole = cv2.bitwise_or(mask_living, mask_necrotic)

    mask_skin_orig = cv2.bitwise_and(
        cv2.inRange(ycrcb_orig, np.array([60, 133, 80]), np.array([255, 175, 130])),
        cv2.inRange(hsv_orig, np.array([0, 25, 50]), np.array([24, 200, 255]))
    )

    global_whole_ratio = np.count_nonzero(mask_whole) / total_img_pixels

    # Jika seluruh citra memiliki proporsi helai daun utuh < 20%, tidak mungkin merupakan diagnosis daun yang valid
    if global_whole_ratio < 0.20:
        return []

    verified = []
    for item in raw_boxes_data:
        x1, y1, x2, y2 = [int(v) for v in item["bbox"]]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(640, x2), min(640, y2)
        if x2 <= x1 + 5 or y2 <= y1 + 5:
            continue

        roi_hsv = hsv_orig[y1:y2, x1:x2]
        roi_pixels = float((x2 - x1) * (y2 - y1))

        # Area konteks ketat 25 piksel di sekeliling kotak pada seluruh helai daun (hijau + kuning + nekrotik)
        ex1, ey1 = max(0, x1 - 25), max(0, y1 - 25)
        ex2, ey2 = min(640, x2 + 25), min(640, y2 + 25)
        exp_whole = mask_whole[ey1:ey2, ex1:ex2]
        exp_pixels = float((ex2 - ex1) * (ey2 - ey1))
        exp_whole_ratio = np.count_nonzero(exp_whole) / exp_pixels

        # Hitung rasio piksel helai daun secara terpisah pada 4 strip luar (lebar 25 px)
        top_strip = mask_whole[max(0, y1 - 25):y1, max(0, x1):min(640, x2)]
        bot_strip = mask_whole[y2:min(640, y2 + 25), max(0, x1):min(640, x2)]
        left_strip = mask_whole[max(0, y1):min(640, y2), max(0, x1 - 25):x1]
        right_strip = mask_whole[max(0, y1):min(640, y2), x2:min(640, x2 + 25)]

        top_r = float(np.count_nonzero(top_strip)) / float(top_strip.size) if top_strip.size > 0 else 0.0
        bot_r = float(np.count_nonzero(bot_strip)) / float(bot_strip.size) if bot_strip.size > 0 else 0.0
        left_r = float(np.count_nonzero(left_strip)) / float(left_strip.size) if left_strip.size > 0 else 0.0
        right_r = float(np.count_nonzero(right_strip)) / float(right_strip.size) if right_strip.size > 0 else 0.0

        surrounding_whole_sides = sum(
            [1 for r in [top_r, bot_r, left_r, right_r] if r >= 0.08]
        )

        roi_green = np.count_nonzero(
            cv2.inRange(roi_hsv, np.array([32, 30, 28]), np.array([92, 255, 255]))
        ) / roi_pixels
        roi_yellow = np.count_nonzero(
            cv2.inRange(roi_hsv, np.array([18, 40, 45]), np.array([32, 255, 255]))
        ) / roi_pixels
        roi_living = roi_green + roi_yellow
        roi_skin = np.count_nonzero(mask_skin_orig[y1:y2, x1:x2]) / roi_pixels

        roi_necrotic = np.count_nonzero(
            cv2.inRange(roi_hsv, np.array([0, 20, 10]), np.array([24, 255, 200]))
        ) / roi_pixels
        roi_dark = np.count_nonzero(
            cv2.inRange(roi_hsv, np.array([0, 0, 0]), np.array([180, 255, 50]))
        ) / roi_pixels
        # Masker bercak kering abu-abu pucat khas pusat Cordana & Pestalotiopsis
        roi_pale_dry = np.count_nonzero(
            cv2.inRange(roi_hsv, np.array([0, 0, 120]), np.array([180, 45, 255]))
        ) / roi_pixels

        cls_name = item["class_name"]
        is_dry_lesion = (roi_pale_dry >= 0.18 or roi_necrotic >= 0.15 or (roi_yellow + roi_dark) >= 0.20)

        # 1. Validasi Penyakit Bercak (Black Sigatoka, Cordana, Pestalotiopsis, Yellow Sigatoka)
        if cls_name in ["Black Sigatoka", "Cordana", "Pestalotiopsis", "Yellow Sigatoka"]:
            # Tolak kotak yang jatuh pada kulit manusia / tangan
            if roi_skin >= 0.20 and roi_green < 0.15:
                continue

            # Anti-pot di bawah daun: kotak bukan lesi kering dengan hijau rendah dan bawah tidak ada daun
            if (not is_dry_lesion) and roi_green < 0.15 and bot_r < 0.08 and (left_r < 0.08 or right_r < 0.08):
                continue

            # Cek Posisi Bawah & Permukaan Polos/Geometris (pot bunga plastik/tanah liat di bagian bawah gambar)
            if y2 >= int(0.85 * 640) and roi_green < 0.03:
                roi_gray = cv2.cvtColor(resized_bgr[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
                roi_lap_var = float(cv2.Laplacian(roi_gray, cv2.CV_64F).var())
                roi_hues = roi_hsv[:, :, 0].flatten()
                roi_hue_std = float(np.std(roi_hues)) if len(roi_hues) > 0 else 0.0
                if roi_hue_std < 12.0 or roi_lap_var < 35.0:
                    continue

            # Daun hijau sehat tanpa gejala penyakit TIDAK BISA didiagnosis sebagai bercak penyakit
            if roi_green >= 0.75 and (roi_necrotic + roi_dark + roi_pale_dry) < 0.05 and roi_yellow < 0.15:
                continue

            # Khusus lesi nekrotik kering (Cordana/Sigatoka/Pestalotiopsis): jika terbukti lesi kering, izinkan
            if not is_dry_lesion:
                if roi_living < 0.05 and exp_whole_ratio < 0.20 and surrounding_whole_sides < 2:
                    continue
                if (roi_necrotic + roi_dark) >= 0.65 and exp_whole_ratio < 0.25 and surrounding_whole_sides < 2:
                    continue

            if global_whole_ratio < 0.30 and surrounding_whole_sides < 2 and not is_dry_lesion:
                if exp_whole_ratio < 0.25 or item["confidence_pct"] < 50.0:
                    continue

        # 2. Validasi Kelas Fresh (Daun Sehat) — Cegah daun tanaman pot dianggap Fresh
        elif cls_name == "Fresh":
            if (
                item["confidence_pct"] < 55.0
                or item["box_area_ratio_pct"] < 25.0
                or roi_green < 0.45
            ):
                continue

        verified.append(item)

    return verified


# ==============================================================================
# 7. FUNGSI CIE-LAB CLAHE & PENGGAMBARAN KOTAK ANTI-TERPOTONG
# ==============================================================================
def apply_cielab_clahe(img_bgr_640: np.ndarray, clip_limit: float = 2.0, tile_size: int = 8) -> np.ndarray:
    lab_img = cv2.cvtColor(img_bgr_640, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab_img)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(tile_size, tile_size))
    l_enhanced = clahe.apply(l_channel)
    merged_lab = cv2.merge((l_enhanced, a_channel, b_channel))
    return cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)


def draw_smart_bounding_boxes(img_bgr: np.ndarray, detections_to_draw: list) -> np.ndarray:
    canvas = img_bgr.copy()
    h, w = canvas.shape[:2]
    occupied_label_rects = []

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

        for (ox1, oy1, ox2, oy2) in occupied_label_rects:
            if not (lx2 < ox1 or lx1 > ox2) and not (ly2 < oy1 or ly1 > oy2):
                ly1 = min(h - box_h_pad - 2, oy2 + 3)
                ly2 = ly1 + box_h_pad

        occupied_label_rects.append((lx1, ly1, lx2, ly2))
        cv2.rectangle(canvas, (lx1, ly1), (lx2, ly2), color, -1)
        cv2.rectangle(canvas, (lx1, ly1), (lx2, ly2), (255, 255, 255), 1)
        cv2.putText(
            canvas, label_text, (lx1 + 5, ly1 + th + 4),
            font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA
        )

    return canvas


def extract_yolo_detections(results) -> list:
    raw_detections = []
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
            area_ratio_pct = ((box_w * box_h) / (640.0 * 640.0)) * 100.0

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
                "bbox": [round(x1, 1), round(y1, 1), round(x2, 1), round(y2, 1)]
            })

    return raw_detections


def encode_bgr_to_base64(img_bgr: np.ndarray) -> str:
    _, buffer = cv2.imencode(".jpg", img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
    return f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"


# ==============================================================================
# 8. ENDPOINT UTAMA WEB & API PREDIKSI (/predict)
# ==============================================================================
@app.route("/")
def index():
    return render_template("index.html", model_loaded=(model is not None), model_path=loaded_model_path)


@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({
            "status": "error",
            "message": "File model 'models/best_yolo26n_clahe.pt' belum ditemukan di server."
        }), 500

    if "image" not in request.files:
        return jsonify({"status": "error", "message": "Tidak ada file gambar yang dikirimkan."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"status": "error", "message": "Nama file kosong."}), 400

    conf_threshold = float(request.form.get("conf_threshold", 0.25))
    iou_threshold = float(request.form.get("iou_threshold", 0.45))
    use_clahe = request.form.get("use_clahe", "true").lower() == "true"

    raw_bytes = file.read()

    # Dekode gambar dengan koreksi otomatis orientasi EXIF kamera HP
    raw_bgr = None
    try:
        pil_img = Image.open(io.BytesIO(raw_bytes))
        pil_img = ImageOps.exif_transpose(pil_img).convert("RGB")
        raw_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    except Exception:
        file_bytes = np.frombuffer(raw_bytes, np.uint8)
        raw_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

    if raw_bgr is None:
        return jsonify({"status": "error", "message": "Format gambar tidak dapat dibaca atau rusak."}), 400

    # --- TAHAP 1: VALIDASI GATEKEEPER (AI, PLASTIK, MANUSIA, TANAH, OBJEK NON-DAUN, DAUN LAIN) ---
    gatekeeper_result = validate_image_gatekeeper(raw_bgr, raw_bytes, file.filename)
    if not gatekeeper_result["valid"]:
        internal_reason = gatekeeper_result.get("internal_reason") or "Gatekeeper: Proporsi helai daun pisang tidak memadai"
        print(f"[PREDICT] File: '{file.filename}' | Status: REJECTED | Reason: {internal_reason} | Raw: 0 | Verified: 0")
        return jsonify({
            "status": "rejected",
            "rejection_type": "non_banana_leaf",
            "title": STANDARD_NON_BANANA_TITLE,
            "reason": STANDARD_NON_BANANA_REASON,
            "metrics": gatekeeper_result
        }), 200

    # --- TAHAP 2: PRAPEMROSESAN (RESIZE 640x640 + CIE-LAB CLAHE) ---
    t0 = time.perf_counter()
    resized_bgr = cv2.resize(raw_bgr, (640, 640), interpolation=cv2.INTER_LINEAR)
    clahe_bgr = apply_cielab_clahe(resized_bgr, clip_limit=2.0, tile_size=8)
    input_for_yolo = clahe_bgr if use_clahe else resized_bgr
    preprocess_ms = (time.perf_counter() - t0) * 1000.0

    # --- TAHAP 3: INFERENSI MODEL YOLO26 NANO & NMS (PASS 1) ---
    t1 = time.perf_counter()
    results = model.predict(
        source=input_for_yolo,
        imgsz=640,
        conf=conf_threshold,
        iou=iou_threshold,
        verbose=False
    )
    inference_nms_ms = (time.perf_counter() - t1) * 1000.0

    # --- TAHAP 4: EKSTRAKSI & VERIFIKASI KOTAK TERHADAP PIKSEL ASLI ---
    t2 = time.perf_counter()
    raw_detections = extract_yolo_detections(results)
    verified_detections = verify_yolo_boxes_against_raw_pixels(resized_bgr, raw_detections)

    # FITUR AUTO-FALLBACK ANTI DOUBLE-CLAHE:
    # Jika use_clahe=True tetapi hasil deteksi kosong, jalankan inferensi cadangan pada citra asli (resized_bgr)
    fallback_infer_ms = 0.0
    if use_clahe and len(verified_detections) == 0:
        fallback_conf = max(0.12, conf_threshold - 0.08)
        t_fb = time.perf_counter()
        fallback_results = model.predict(
            source=resized_bgr,
            imgsz=640,
            conf=fallback_conf,
            iou=iou_threshold,
            verbose=False
        )
        fallback_infer_ms = (time.perf_counter() - t_fb) * 1000.0
        inference_nms_ms += fallback_infer_ms

        fallback_raw = extract_yolo_detections(fallback_results)
        fallback_verified = verify_yolo_boxes_against_raw_pixels(resized_bgr, fallback_raw)
        if len(fallback_verified) > 0:
            verified_detections = fallback_verified
            raw_detections = fallback_raw
            input_for_yolo = resized_bgr

    # --- TAHAP 5: PENOLAKAN OTOMATIS PASCA-YOLO UNTUK DAUN TANAMAN LAIN & PEMANDANGAN ---
    is_invalid_scene = False
    rejection_detail_internal = ""

    if len(verified_detections) > 0:
        max_det_conf = max(d["confidence_pct"] for d in verified_detections)
        m_solidity = gatekeeper_result.get("solidity", 1.0)
        m_blob = gatekeeper_result.get("living_blob_ratio", 1.0)
        m_largest_blob = gatekeeper_result.get("largest_blob_ratio", 1.0)
        m_living_leaf = gatekeeper_result.get("living_leaf_ratio", 1.0)
        m_whole_leaf = gatekeeper_result.get("botanical_ratio", 1.0)

        # Kasus A: Hanya terdeteksi Fresh tetapi morfologinya terfragmentasi / daun kecil
        if all(d["class_name"] == "Fresh" for d in verified_detections):
            if max_det_conf < 68.0 and m_solidity < 0.60 and m_blob < 0.22:
                is_invalid_scene = True
                rejection_detail_internal = "Pasca-YOLO: Deteksi Fresh pada daun terfragmentasi (bukan lamina pisang)"

        # Kasus B: Deteksi penyakit (Black Sigatoka dll.) pada citra pemandangan/tanah/kayu di mana lamina daun utuh tidak ada
        elif (m_whole_leaf < 0.20 and m_living_leaf < 0.16) or m_largest_blob < 0.18 or (m_blob < 0.15 and max_det_conf < 70.0):
            is_invalid_scene = True
            rejection_detail_internal = f"Pasca-YOLO: Deteksi bercak pada latar pemandangan/tanah/kayu tanpa lamina utuh (whole={m_whole_leaf*100:.1f}%, blob={m_largest_blob*100:.1f}%)"

    if len(verified_detections) == 0 or is_invalid_scene:
        internal_reason = rejection_detail_internal or (
            "YOLO: 0 deteksi terverifikasi" if len(verified_detections) == 0 else "YOLO: Daun terfragmentasi / non-pisang"
        )
        print(f"[PREDICT] File: '{file.filename}' | Status: REJECTED | Reason: {internal_reason} | Raw: {len(raw_detections)} | Verified: {len(verified_detections)}")
        return jsonify({
            "status": "rejected",
            "rejection_type": "non_banana_leaf",
            "title": STANDARD_NON_BANANA_TITLE,
            "reason": STANDARD_NON_BANANA_REASON,
            "metrics": {
                "total_detections": 0,
                "raw_detections_count": len(raw_detections),
                "internal_reason": internal_reason,
                "green_yellow_pct": gatekeeper_result.get("green_yellow_pct", 0.0),
                "botanical_pct": gatekeeper_result.get("botanical_pct", 0.0)
            }
        })

    # Susun ulang ID, hitung granularitas & gambar bounding box
    detections = []
    detections_to_draw = []
    lesion_level_count = 0
    leaf_level_count = 0
    class_counts = {}

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
            "label_text": label_text
        })
        detections.append(d)

    annotated_bgr = draw_smart_bounding_boxes(input_for_yolo, detections_to_draw)

    orig_b64 = encode_bgr_to_base64(resized_bgr)
    clahe_b64 = encode_bgr_to_base64(clahe_bgr)
    annotated_b64 = encode_bgr_to_base64(annotated_bgr)

    postprocess_ms = max(0.0, ((time.perf_counter() - t2) * 1000.0) - fallback_infer_ms)
    server_total_ms = preprocess_ms + inference_nms_ms + postprocess_ms

    # Penentuan kelas patogen dominan berdasarkan prioritas tingkat keganasan patogen
    dominant_class = None
    agronomy_advice = None
    if len(detections) > 0:
        priority_order = ["Black Sigatoka", "Yellow Sigatoka", "Cordana", "Pestalotiopsis", "Fresh"]
        detected_classes = {d["class_name"] for d in detections}
        dominant_class = next((c for c in priority_order if c in detected_classes), "Fresh")
        agronomy_advice = AGRONOMY_KB.get(dominant_class, AGRONOMY_KB["Fresh"])

    print(f"[PREDICT] File: '{file.filename}' | Status: VALID | Dominant: {dominant_class} | Raw: {len(raw_detections)} | Verified: {len(detections)}")

    return jsonify({
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
            "server_total_ms": round(server_total_ms, 2)
        },
        "images": {
            "original_b64": orig_b64,
            "clahe_b64": clahe_b64,
            "annotated_b64": annotated_b64
        }
    })


# ==============================================================================
# 9. ENDPOINT SAMPEL GAMBAR DAUN PISANG (FOLDER TEMPLATES & STATIC)
# ==============================================================================
@app.route("/api/samples", methods=["GET"])
def get_sample_images():
    """
    Memindai semua file gambar berekstensi .jpg, .jpeg, .png, .webp
    di folder 'templates' (dan subfolder) serta 'static/samples'
    untuk daftar pengujian instan di UI.
    """
    samples = []
    seen_names = set()

    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    if os.path.exists(templates_dir):
        for root, _, files in os.walk(templates_dir):
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in VALID_IMAGE_EXTS and f not in seen_names:
                    rel_path = os.path.relpath(os.path.join(root, f), templates_dir).replace("\\", "/")
                    samples.append({
                        "filename": rel_path,
                        "name": f,
                        "url": f"/sample-file/{rel_path}",
                        "source": "templates"
                    })
                    seen_names.add(f)

    static_samples_dir = os.path.join(os.path.dirname(__file__), "static", "samples")
    if os.path.exists(static_samples_dir):
        for f in os.listdir(static_samples_dir):
            ext = os.path.splitext(f)[1].lower()
            if ext in VALID_IMAGE_EXTS and f not in seen_names:
                samples.append({
                    "filename": f,
                    "name": f,
                    "url": f"/sample-file/{f}",
                    "source": "static"
                })
                seen_names.add(f)

    return jsonify({"success": True, "samples": samples, "total": len(samples)})


@app.route("/sample-file/<path:filename>", methods=["GET"])
def serve_sample_file(filename):
    """
    Mengirimkan file gambar sampel dari folder 'templates' (atau 'static/samples' sebagai fallback)
    hanya untuk ekstensi gambar yang valid.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in VALID_IMAGE_EXTS:
        return jsonify({"error": "Tipe file tidak diizinkan"}), 403

    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    target_path = os.path.join(templates_dir, filename)
    if os.path.exists(target_path):
        return send_from_directory(templates_dir, filename)

    static_samples_dir = os.path.join(os.path.dirname(__file__), "static", "samples")
    target_static = os.path.join(static_samples_dir, os.path.basename(filename))
    if os.path.exists(target_static):
        return send_from_directory(static_samples_dir, os.path.basename(filename))

    return jsonify({"error": "File sampel tidak ditemukan", "filename": filename}), 404


@app.route("/deteksi", methods=["GET"])
def deteksi():
    return render_template("deteksi.html")


@app.route("/katalog-patogen", methods=["GET"])
def katalog_patogen():
    """
    Halaman ensiklopedia dan katalog patogen daun pisang lengkap.
    """
    return render_template("katalog_patogen.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)