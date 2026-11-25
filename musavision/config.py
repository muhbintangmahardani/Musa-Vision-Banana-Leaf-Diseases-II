"""Application configuration, file paths, and inference constants for MusaVision."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
SAMPLES_DIR = STATIC_DIR / "samples"

MODEL_PATHS: tuple[Path, ...] = (
    BASE_DIR / "models" / "best_yolo26n_clahe.pt",
    BASE_DIR / "best_yolo26n_clahe.pt",
    BASE_DIR / "models" / "best.pt",
    BASE_DIR / "best.pt",
    BASE_DIR / "models" / "yolo26n.pt",
)

MAX_CONTENT_LENGTH = 16 * 1024 * 1024
VALID_IMAGE_EXTS: frozenset[str] = frozenset({".jpg", ".jpeg", ".png", ".webp"})

# Inference and CIE-LAB CLAHE defaults
DEFAULT_CONF_THRESHOLD = 0.25
DEFAULT_IOU_THRESHOLD = 0.45
DEFAULT_USE_CLAHE = True
YOLO_IMAGE_SIZE = 640
CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_SIZE = 8
JPEG_OUTPUT_QUALITY = 92
FALLBACK_MIN_CONF = 0.12
FALLBACK_CONF_DROP = 0.08

# Standardized user-facing rejection payload copy
STANDARD_NON_BANANA_TITLE = "Objek Bukan Daun Pisang"
STANDARD_NON_BANANA_REASON = (
    "Citra yang diunggah teridentifikasi sebagai objek bukan daun pisang. "
    "Mohon fokuskan kamera pada permukaan helai daun pisang (Musa spp.) "
    "tanpa menyertakan pot, manusia, atau objek lain."
)

# Color thresholds (HSV / YCrCb) used across pre-YOLO and post-YOLO validation
HSV_SKIN_LOWER = (0, 25, 50)
HSV_SKIN_UPPER = (24, 200, 255)
YCRCB_SKIN_LOWER = (60, 133, 80)
YCRCB_SKIN_UPPER = (255, 175, 130)

HSV_GREEN_LOWER = (32, 30, 28)
HSV_GREEN_UPPER = (92, 255, 255)
HSV_YELLOW_LOWER = (18, 40, 45)
HSV_YELLOW_UPPER = (32, 255, 255)
HSV_NECROTIC_LOWER = (4, 25, 20)
HSV_NECROTIC_UPPER = (22, 255, 195)
HSV_ROI_NECROTIC_LOWER = (0, 20, 10)
HSV_ROI_NECROTIC_UPPER = (24, 255, 200)
HSV_PITCH_DARK_LOWER = (0, 0, 0)
HSV_PITCH_DARK_UPPER = (180, 255, 42)
HSV_ROI_DARK_LOWER = (0, 0, 0)
HSV_ROI_DARK_UPPER = (180, 255, 50)
HSV_PALE_DRY_LOWER = (0, 0, 120)
HSV_PALE_DRY_UPPER = (180, 45, 255)
HSV_SPECULAR_LOWER = (0, 0, 220)
HSV_SPECULAR_UPPER = (180, 30, 255)
HSV_WATER_BLUE_LOWER = (92, 30, 40)
HSV_WATER_BLUE_UPPER = (135, 255, 255)

# ImageNet keywords flagging obvious non-leaf objects, humans, food, scenery, and household items
REJECTED_NON_LEAF_KEYWORDS: list[str] = [
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
    "lakeside", "seashore", "promontory", "sandbar", "breakwater", "pier", "dock", "dam",
    "canoe", "paddle", "gondola", "speedboat", "lifeboat", "airship", "boathouse",
    "beacon", "lighthouse", "fountain", "geyser", "water bottle", "water jug", "water tower",
    "valley", "cliff", "alp", "volcano", "mountain tent", "mountain bike",
    "stone wall", "megalith", "quarry", "dirt", "soil", "earth", "gravel", "sand", "mud",
    "park bench", "street", "road", "highway", "bridge", "building", "house", "barn",
    "roof", "fence", "worm fence", "chainlink fence", "pole", "sign", "trash", "ashcan",
    "wooden spoon", "lumber", "log",
]

# ImageNet classes frequently confused with banana leaf ribs or fungal blotches
LEAF_CONFUSION_CATEGORIES: frozenset[str] = frozenset({
    "tree frog", "bullfrog", "tailed frog", "leafhopper", "vine snake", "quill", "sea anemone",
    "shower curtain", "theater curtain", "mosquito net", "velvet", "window shade",
    "jigsaw puzzle", "coral fungus", "agaric", "bolete", "banana", "ear", "corn",
    "zucchini", "cucumber", "head cabbage", "artichoke", "broccoli", "rapeseed",
    "green lizard", "sulphur butterfly", "American chameleon", "flatworm", "mud turtle",
    "box turtle", "terrapin", "agama", "alligator lizard", "garter snake", "water snake",
    "grasshopper", "mantis", "cicada", "tray", "spaghetti squash", "butternut squash",
    "acorn squash", "hen-of-the-woods",
})

POT_AND_OTHER_PLANT_KEYWORDS: list[str] = [
    "pot", "flowerpot", "vase", "planter", "greenhouse",
    "daisy", "rose", "sunflower", "tulip", "orchid", "lily", "hibiscus",
    "broccoli", "cauliflower", "head cabbage", "bell pepper", "cucumber",
    "zucchini", "strawberry", "pineapple", "pomegranate", "acorn", "maple", "oak",
    "picket fence", "patio", "window", "curtain", "table", "desk", "chair", "couch",
    "bucket", "basket", "barrel", "crate",
    "terracotta", "urn", "tub", "mortar", "ashcan", "trash", "potted", "porch",
    "tile", "floor", "wall", "brick", "ceramic", "clay", "plastic bag",
]

POT_SENSITIVE_KEYWORDS: frozenset[str] = frozenset({
    "pot", "flowerpot", "vase", "planter", "greenhouse", "houseplant", "bonsai",
    "daisy", "rose", "sunflower", "tulip", "orchid", "lily", "hibiscus", "earthstar",
    "terracotta", "urn", "tub", "mortar", "potted", "ashcan", "trash", "bucket",
    "basket", "barrel", "crate", "table", "desk", "chair", "couch", "ceramic", "clay",
})

AI_FILENAME_KEYWORDS: list[str] = [
    "midjourney", "dall-e", "dalle", "stable diffusion", "stablediffusion",
    "sdxl", "comfyui", "automatic1111", "bing image creator", "firefly",
    "adobe firefly", "leonardo.ai", "ideogram", "novelai", "ai_generated", "ai-generated",
]

AI_METADATA_KEYWORDS: list[str] = [
    "trainedalgorithmicmedia", "digitalsourcetype/trainedalgorithmicmedia",
    "midjourney", "dall-e", "dalle", "stablediffusion", "stable diffusion", "comfyui",
    "automatic1111", "adobe firefly", "leonardo.ai", "ideogram", "novelai",
]

AI_DIFFUSION_PARAM_TERMS: tuple[str, ...] = (
    "steps:", "sampler:", "cfg scale:", "seed:",
    "ksampler", "checkpointloader", "--ar", "--v 5", "--v 6",
)

EXACT_AI_RESOLUTIONS: frozenset[tuple[int, int]] = frozenset({
    (1024, 1024), (1024, 1792), (1792, 1024), (1024, 1536), (1536, 1024),
    (1344, 768), (768, 1344), (512, 512), (768, 768), (2048, 2048),
})
