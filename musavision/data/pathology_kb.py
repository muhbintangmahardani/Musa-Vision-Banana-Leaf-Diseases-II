"""Banana leaf pathology knowledge base: symptoms, deleafing protocols, and FRAC schedules."""

from typing import Any

SEVERITY_PRIORITY_ORDER: tuple[str, ...] = (
    "Black Sigatoka",
    "Yellow Sigatoka",
    "Cordana",
    "Pestalotiopsis",
    "Fresh",
)

AGRONOMY_KB: dict[str, dict[str, Any]] = {
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
        ),
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
            "Gunakan Fungisida Sistemik Kuratif golongan Triazol (Difenoconazole / Tebuconazole \u2014 [Kode FRAC 3]) "
            "yang dirotasi dengan golongan Strobilurin (Azoxystrobin \u2014 [Kode FRAC 11]) untuk menghentikan "
            "pertumbuhan jamur di dalam jaringan daun."
        ),
        "frac_codes": ["FRAC 3 (Triazol: Difenoconazole/Tebuconazole)", "FRAC 11 (Strobilurin: Azoxystrobin)"],
        "ppl_disclaimer": (
            "PERINGATAN PPL/POPT: Wajib melakukan rotasi bahan aktif antar-kode FRAC agar jamur tidak kebal (resisten). "
            "Konsultasikan dosis penyemprotan dengan Penyuluh Pertanian Lapangan (PPL) atau petugas POPT setempat."
        ),
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
        ),
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
        ),
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
        ),
    },
}


def normalize_class_name(raw_name: str) -> str:
    """Map raw YOLO model class labels to canonical MusaVision class names."""
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
