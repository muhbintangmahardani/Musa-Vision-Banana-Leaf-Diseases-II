# PRODUCT REQUIREMENTS DOCUMENT (PRD) — MUSAVISION V2.1 (EDITORIAL UI OVERHAUL)
**Nama Sistem:** MusaVision: Sistem Deteksi Penyakit Daun Pisang Berbasis YOLO26 Nano & CIE-LAB CLAHE
**File Bobot Model Utama:** `models/best_yolo26n_clahe.pt`
**Acuan Visual:** `DESIGN.md` (TaniScan Editorial Agritech Style — Zero Emoji, Clean Minimalist)

---

## 1. Aturan Kritis Pengembangan (Non-Negotiable Rules)
1. **JANGAN UBAH LOGIKA `app.py`:** Seluruh logika di dalam `app.py` (pemuatan model `best_yolo26n_clahe.pt`, Gatekeeper 4-Lapis, detektor AI, detektor daun tanaman lain, CIE-LAB CLAHE, verifikasi piksel pasca-YOLO, `draw_smart_bounding_boxes`, dan endpoint `POST /predict`) **SUDAH FINAL DAN DILARANG DIUBAH**.
2. **ROMBAK TOTAL `templates/index.html`:** Ganti seluruh tampilan lama dengan tata letak editorial satu halaman penuh (*single-page editorial & workspace*) yang mengacu 100% pada `DESIGN.md` dan gambar referensi.
3. **LARANGAN EMOJI & AI SLOP:** Tidak boleh ada satu pun karakter emoji di dalam kode `templates/index.html`. Semua judul penolakan (`data.title`) yang diterima dari `app.py` harus dibersihkan dari karakter emoji menggunakan fungsi JavaScript `stripEmojis()` sebelum dirender ke DOM.

---

## 2. Kontrak Integrasi Data (`templates/index.html` ↔ `app.py`)
Antarmuka baru wajib tetap mengirim dan menerima seluruh parameter berikut secara akurat:

### 2.1. Input Request (`POST /predict` via `FormData`)
- `image`: Objek file gambar dari klik unggah, *drag-and-drop*, atau kamera HP (`capture="environment"`).
- `conf_threshold`: Nilai slider (`0.25` – `0.85`, default `0.35`).
- `use_clahe`: Nilai checkbox/switch (`"true"` atau `"false"`, default `"true"`).
- `bypass_gatekeeper`: Nilai checkbox (`"true"` atau `"false"`, default `"false"`).

### 2.2. Penanganan Respons JSON dari `app.py`
1. **Status `"rejected"` (Ditolak Gatekeeper):**
   - Tampilkan kartu peringatan minimalis beraksen merah tua (`#B91C1C`) tanpa emoji.
   - Tampilkan `stripEmojis(data.title)` sebagai judul, `data.reason` sebagai penjelasan, serta `data.rejection_type` dan `data.metrics.green_yellow_pct` dalam format monospasi.
2. **Status `"no_detection"` (Tidak Ada Kotak Deteksi):**
   - Tampilkan pesan bersih yang meminta pengguna memastikan foto menampilkan permukaan helai daun pisang secara fokus (tanpa menyuruh menurunkan slider ke 0.15).
3. **Status `"success"` (Deteksi Berhasil):**
   - **Visualisasi Citra:** Tampilkan gambar hasil deteksi (`data.images.annotated_b64`) sebagai visual utama di Kartu Vonis, disertai tombol tab instan untuk melihat `Citra Asli` (`data.images.original_b64`), `CIE-LAB CLAHE` (`data.images.clahe_b64`), atau `Mode Perbandingan 3-Panel`.
   - **Kartu Vonis (Verdict Card):**
     - Nama kelas dominan (`data.agronomy.display_name`) & nama ilmiah (`data.agronomy.scientific_name`).
     - *Progress bar* persentase keyakinan tertinggi dari `data.detections` beserta kategori keparahan (`data.agronomy.severity_category`).
     - Rincian **Protokol Sanitasi / Deleafing** (`data.agronomy.deleafing_protocol`), **Rekomendasi Fungisida Kode FRAC** (`data.agronomy.frac_codes` & `data.agronomy.frac_recommendation`), serta **Peringatan PPL/POPT** (`data.agronomy.ppl_disclaimer`).
   - **Granularitas & Tabel Koordinat:**
     - Tampilkan angka `data.total_detections`, `data.lesion_level_count` (Level Bercak < 35%), dan `data.leaf_level_count` (Level Helai Daun ≥ 35%).
     - Render seluruh baris `data.detections` ke dalam tabel rincian koordinat.
   - **Telemetri Latensi End-to-End:**
     - Tampilkan `preprocess_ms`, `inference_nms_ms`, `postprocess_ms`, `server_total_ms`, dan `client_roundtrip_ms`.

---

## 3. Fitur Tambahan yang Wajib Tetap Ada
1. **Filter Katalog Patogen Interaktif:** Menampilkan 5 kelas kondisi daun pisang yang dapat difilter berdasarkan kategori (`Semua`, `Jamur Ganas Utama`, `Jamur Sekunder`, `Sehat Optimal`).
2. **Log Riwayat Uji Kebun & Ekspor `.CSV`:** Menyimpan riwayat pemindaian di `localStorage` dan mengekspornya ke file `riwayat_uji_kebun_musavision.csv`.
3. **Kalkulator Kuesioner SUS (10 Pernyataan) & Ekspor `.CSV`:** Menghitung skor *System Usability Scale* secara otomatis dan mengekspor rekapitulasi responden ke `rekap_kuesioner_sus_musavision.csv`.