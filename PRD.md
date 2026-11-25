# PRODUCT REQUIREMENTS DOCUMENT (PRD) — MUSAVISION V2.0
**Nama Sistem:** MusaVision: Aplikasi Web Deteksi Penyakit Daun Pisang Berbasis YOLO26 Nano & CIE-LAB CLAHE
**File Bobot Model Utama:** `models/best_yolo26n_clahe.pt`
**Target Pengguna:** Petani Kebun Pisang & Penyuluh Pertanian Lapangan (PPL) (Mobile-First Responsive Web)

## 1. Tujuan Utama & Arsitektur Sistem
Membangun aplikasi web Client-Server menggunakan Python Flask (`app.py`) sebagai Backend dan HTML5 + Tailwind CSS + Vanilla JavaScript (`templates/index.html`) sebagai Frontend yang memuat bobot model hasil pelatihan Kaggle (`models/best_yolo26n_clahe.pt`).
Logika deteksi, prapemrosesan CIE-LAB CLAHE, dan validasi Gatekeeper 2-Lapis sudah dikunci secara permanen di dalam `app.py` dan TIDAK BOLEH diubah.

## 2. Daftar Kelas Deteksi & Granularitas Anotasi
Model `models/best_yolo26n_clahe.pt` mendeteksi 5 kelas kondisi daun pisang yang dibagi menjadi dua kategori granularitas berdasarkan Box Area Ratio terhadap resolusi 640x640 piksel:
1. **Level Helai Daun (Leaf-Level — Rasio Luas Kotak >= 35% atau Kelas Daun Utuh):**
   - `Fresh` (Daun Sehat — warna indikator Hijau `#16a34a`)
   - `Yellow Sigatoka` (Sigatoka Kuning / *Pseudocercospora musae* — warna indikator Kuning `#eab308`)
2. **Level Bercak / Lesi (Lesion-Level — Rasio Luas Kotak < 35%):**
   - `Black Sigatoka` (Sigatoka Hitam / *Pseudocercospora fijiensis* — warna indikator Merah `#dc2626`)
   - `Cordana` (Bercak Daun Cordana / *Cordana musae* — warna indikator Oranye `#f97316`)
   - `Pestalotiopsis` (Bercak Daun Pestalotiopsis / *Pestalotiopsis microspora* — warna indikator Ungu `#8b5cf6`)

## 3. Spesifikasi Kontrak API (`POST /predict` di `app.py`)
### Input Form-Data:
- `image`: File gambar (JPG/PNG/WEBP) dari upload galeri atau kamera belakang HP.
- `conf_threshold`: Float (`0.15` s.d. `0.85`, default `0.25`).
- `iou_threshold`: Float (default `0.45`).
- `use_clahe`: String boolean (`"true"` atau `"false"`, default `"true"`).
- `bypass_gatekeeper`: String boolean (`"true"` atau `"false"`, default `"false"`).

### Output JSON:
1. **Jika Ditolak Gatekeeper (`status: "rejected"`):**
   - `reason`: Pesan penolakan (misalnya terdeteksi wajah selfie manusia atau objek non-daun).
   - `metrics.green_yellow_pct` & `metrics.botanical_pct`: Persentase piksel spektrum botani daun.
2. **Jika Berhasil (`status: "success"` atau `"no_detection"`):**
   - `total_detections`, `lesion_level_count`, `leaf_level_count`, `class_counts`, `dominant_class`.
   - `agronomy`: Objek berisi `display_name`, `scientific_name`, `severity_category`, `symptoms`, `deleafing_protocol`, `frac_recommendation`, `frac_codes` (array), dan `ppl_disclaimer`.
   - `detections`: Array rincian tiap kotak (`id`, `class_name`, `confidence_pct`, `box_area_ratio_pct`, `granularity`, `bbox`).
   - `telemetry`: Objek berisi `preprocess_ms`, `inference_nms_ms`, `postprocess_ms`, dan `server_total_ms`.
   - `images`: Objek berisi `original_b64`, `clahe_b64`, dan `annotated_b64`.

## 4. Kebutuhan Antarmuka Pengguna (`templates/index.html`)
1. **Header & Status Model:** Menampilkan nama aplikasi MusaVision, indikator status model (`models/best_yolo26n_clahe.pt` aktif), dan navigasi 3 Tab: (1) Deteksi & Diagnosis, (2) Riwayat Uji Kebun (.CSV), (3) Evaluasi Kuesioner SUS.
2. **Panel Input & Pengaturan Parameter:**
   - Area Drag & Drop gambar + Tombol "Ambil Foto Kamera HP" (`accept="image/*" capture="environment"`).
   - Toggle Switch "Aktifkan Penajaman CIE-LAB CLAHE" (`use_clahe`, default ON).
   - Slider "Confidence Threshold" (`0.15` - `0.85`, default `0.25`).
   - Checkbox "Bypass Gatekeeper (Khusus Uji Dataset)" (`bypass_gatekeeper`, default OFF).
3. **Banner Penolakan Gatekeeper (Alert Merah):** Tampil jelas jika `status === "rejected"` (saat uji selfie wajah atau objek non-daun) beserta nilai persentase piksel klorofil/botani.
4. **Visualisasi 3-Panel Berdampingan:**
   - Panel 1: Citra Asli (`640x640`).
   - Panel 2: Citra Penajaman CIE-LAB CLAHE (Kanal $L$, `clipLimit=2.0`, `tileGridSize=8x8`).
   - Panel 3: Hasil Deteksi Bounding Box YOLO26 Nano.
5. **Kartu Ringkasan Deteksi & Granularitas Anotasi:**
   - Memisahkan secara visual angka **Jumlah Titik Bercak (Lesion-Level)** dan **Jumlah Cakupan Helai Daun (Leaf-Level)**.
   - Tabel rincian seluruh kotak deteksi (`No`, `Kelas`, `Confidence (%)`, `Rasio Luas Box (%)`, `Level Anotasi`, `Koordinat Box`).
6. **Kartu Rekomendasi Agronomi, Sanitasi (Deleafing), & Kode FRAC:**
   - Menampilkan gejala, langkah pemangkasan sanitasi (jaga minimal 6-8 daun sehat), badge Kode Fungisida FRAC (`FRAC M03/M05` atau `FRAC 3 & FRAC 11`), serta kotak kuning Peringatan PPL/POPT.
7. **Panel Telemetri Latensi End-to-End (ms):**
   - Menampilkan `Preprocess (ms)`, `Inference + NMS (ms)`, `Postprocess (ms)`, `Total Server (ms)`, dan `Client Roundtrip (ms)` yang dihitung menggunakan `performance.now()` di browser.
8. **Tab Riwayat Uji Kebun & Export CSV:**
   - Menyimpan setiap hasil pengujian ke `localStorage`, menampilkannya dalam tabel riwayat, dan menyediakan tombol "Download CSV" untuk lampiran Bab IV skripsi.
9. **Tab Kalkulator System Usability Scale (SUS):**
   - Menampilkan 10 pernyataan baku SUS (Brooke) dalam bahasa Indonesia dengan pilihan skala Likert 1 s.d. 5.
   - Menghitung otomatis rumus `Skor SUS = ((Jumlah Ganjil - 5) + (25 - Jumlah Genap)) * 2.5`, menampilkan kategori kelayakan (`>= 68 Layak/Good`, `>= 80.3 Sangat Baik/Excellent`), serta menyimpan daftar responden SUS dan mengekspornya ke `.CSV`.
