# Product Requirements Document (PRD)
## Redesign UI/UX Frontend MusaVision — Editorial Smart Farming Platform

| Atribut | Detail |
| :--- | :--- |
| **Nama Produk** | MusaVision (Sistem Deteksi Penyakit Daun Pisang Berbasis Web) |
| **Versi Dokumen** | v2.0 — Editorial Redesign & Motion Architecture |
| **Teknologi Inti** | Flask Backend (Fixed) · YOLO26 Nano · CIE-LAB CLAHE · Gatekeeper Validasi |
| **Stack Frontend** | HTML5 Semantik · CSS3 Modern (Design Tokens) · Vanilla JS (ES Modules) |
| **Stack Animasi** | Lenis (Smooth Scroll) · GSAP + ScrollTrigger (Word Reveal) · Motion (Card & Hover) |
| **Referensi Estetika** | Konsep Editorial *Agrovia Smart Farming Platform* (Hangat, Kredibel, Humanis) |

---

## 1. Latar Belakang & Tujuan Redesign

Sebagian besar antarmuka aplikasi pertanian berbasis AI terlihat terlalu teknis, kaku, dan jauh dari realitas petani di kebun. *Redesign* ini bertujuan menjembatani kecanggihan deteksi objek **YOLO26 Nano + CIE-LAB CLAHE** dengan pengalaman visual editorial yang hangat, organik, mudah dipahami petani di lapangan, sekaligus tampil meyakinkan saat demonstrasi sidang skripsi.

### Sasaran Utama
1. **Kredibilitas Instan (*Above-the-Fold*):** Menghadirkan *cinematic hero* berbasis foto asli daun/kebun pisang dengan lencana kepercayaan nyata (Skor SUS, jumlah kelas patologi, dan arsitektur model).
2. **Kemudahan Bagi Petani:** Menyederhanakan alur deteksi (*Upload / Kamera* -> *Hasil & Tindakan Sanitasi FRAC*) dengan menyembunyikan parameter teknis ke dalam panel lipat khusus peneliti (`<details>`).
3. **Interaksi Modern & Halus:** Menerapkan *smooth scrolling* (Lenis), tipografi judul muncul per kata saat di-*scroll* (GSAP + ScrollTrigger), dan animasi kartu responsif (Motion) tanpa mengorbankan performa di ponsel petani.

---

## 2. Batasan Mutlak (*Non-Negotiable Constraints*)

1. **Dilarang Mengubah `app.py`:** Seluruh logika backend (model YOLO26 Nano `best_yolo26n_clahe.pt`, prapemrosesan CIE-LAB CLAHE, Gatekeeper anti objek non-daun/pot/manusia, Dual-Pass Fallback, prioritas keganasan patogen, penamaan penolakan seragam **"Objek Bukan Daun Pisang"**, serta rute API) **tidak boleh diubah sama sekali**.
2. **Ruang Lingkup File yang Dimodifikasi:**
   - `templates/index.html`
   - `static/css/style.css`
   - `static/js/main.js`
   - `templates/katalog_patogen.html` *(penyelarasan navbar, palet warna, dan tipografi agar seragam)*
3. **Hapus Bagian Testimonial:** Tidak boleh ada bagian *testimonial*, *review*, atau kutipan fiktif pengguna di halaman mana pun.
4. **Wajib Menggunakan Aset Lokal Sendiri:** Dilarang menyalin atau menautkan foto milik referensi eksternal (Agrovia) ke dalam kode produksi. Gunakan aset lokal yang sudah tersedia di `static/samples/` dan `templates/samples/`.

---

## 3. Sistem Desain Visual (*Editorial Agritech Design System*)

### 3.1 Palet Warna (*CSS Custom Properties*)
```css
:root {
  --bg-canvas: #F7F6F1;        /* Warm Alabaster — latar halaman utama */
  --bg-surface: #FFFFFF;       /* Crisp White — kartu workspace & informasi */
  --bg-forest: #12261C;        /* Deep Forest Green — hero overlay, aksen gelap, footer */
  --bg-forest-soft: #1C382A;   /* Elevated Forest — elemen kartu di latar gelap */
  --accent-green: #2F6B43;     /* Organic Botanical Green — CTA utama & status Fresh */
  --accent-green-hover: #245434;
  --accent-gold: #C88A2E;      /* Harvest Gold — lencana metrik & Yellow Sigatoka */
  --accent-terracotta: #B84A39;/* Alert Terracotta — peringatan Black Sigatoka & penolakan */
  --text-primary: #14221B;     /* Teks utama kontras tinggi */
  --text-secondary: #4D5E55;   /* Teks deskripsi */
  --border-subtle: #E5E3DC;    /* Garis tepi organik halus */
}
```

### 3.2 Tipografi
- **Heading / Display Serif:** `Instrument Serif` atau `Fraunces` (Google Fonts) — menciptakan kesan editorial yang berwibawa dan hangat.
- **Body & UI Sans-Serif:** `Plus Jakarta Sans` (Google Fonts) — keterbacaan tinggi untuk instruksi petani, label form, tabel deteksi, dan angka telemetri.
- **Monospace (Opsional untuk Telemetri & Kode FRAC):** `JetBrains Mono`.

### 3.3 Aset Visual Lokal yang Digunakan
- **Hero Background:** `/static/samples/musavision_hero_bg.jpg` (cadangan: `/static/samples/banana_hero_dark.jpg`).
- **3 Pilar Tindakan Sanitasi (*Smart Farming Solutions*):**
  1. `/static/samples/pillar_sanitation_deleafing.jpg`
  2. `/static/samples/pillar_frac_spraying.jpg`
  3. `/static/samples/pillar_canopy_management.jpg`
- **5 Sampel Uji Instan:** Hanya berkas berawalan `sample_` (`sample_black_sigatoka.jpg`, `sample_cordana.jpg`, `sample_fresh.jpg`, `sample_pestalotiopsis.jpg`, `sample_yellow_sigatoka.jpg`).

---

## 4. Arsitektur Halaman & Spesifikasi Section (`templates/index.html`)

### Section 1: Sticky Minimalist Navbar
- Posisi `fixed` di atas *hero* dengan latar transparan; berubah menjadi *frosted alabaster* (`rgba(247, 246, 241, 0.92)` + `backdrop-filter: blur(12px)`) saat di-*scroll* melewati 40 px.
- **Kiri:** Brand mark **MusaVision** + indikator status model halus dari Jinja (`{{ model_loaded }}`).
- **Tengah:** Tautan navigasi halus (`Beranda`, `Misi`, `Deteksi AI`, `Sanitasi Kebun`, `Katalog Patogen` -> `/katalog-patogen`).
- **Kanan:** Tombol CTA pill **"Mulai Deteksi"** (scroll halus ke `#deteksi` menggunakan `lenis.scrollTo`) + menu drawer responsif untuk mobile.

### Section 2: Cinematic Hero Section (`#beranda`)
- Tata letak *full-bleed* (`min-height: 92vh`) dengan latar `/static/samples/musavision_hero_bg.jpg` dan *dark botanical gradient overlay*.
- **Trust Badge Above-the-Fold:** Lencana *glassmorphism* hangat menampilkan data kredibilitas nyata penelitian:
  - `SUS Score 84,0 (Excellent)` · `5 Kelas Patologi Daun` · `YOLO26 Nano + CIE-LAB CLAHE`
- **Headline Editorial (Animasi Muncul Per Kata):**
  *"Deteksi Cerdas untuk Kesehatan Kebun Pisang Masa Depan."*
- **Subheadline:** Penjelasan ringkas bahwa sistem membantu petani mengenali bercak daun sejak dini dan mengambil tindakan sanitasi serta fungisida yang tepat.
- **Dual CTA:**
  - **Primary CTA:** `Mulai Deteksi Daun` (mengarah halus ke `#deteksi`).
  - **Secondary CTA:** `Panduan Sanitasi & FRAC` (mengarah halus ke `#sanitasi`).

### Section 3: Credibility & Technology Standards Strip
- Menggantikan *partner brand strip* dengan 5 pilar teknologi dan standar agronomi yang menopang sistem:
  - `YOLO26 Nano Detection`
  - `CIE-LAB CLAHE Contrast`
  - `Gatekeeper Validasi Citra`
  - `Standar Rotasi Kode FRAC`
  - `Protokol Deleafing 6-8 Daun`

### Section 4: Mission Section (`#misi`)
- Tata letak editorial 2 kolom asimetris dengan ruang napas luas.
- **Judul (Word Reveal):** *"Dibangun untuk Mendampingi Petani Menjaga Produktivitas Lahan."*
- **Konten:** Menjelaskan secara membumi dampak serangan jamur daun (*Black Sigatoka*, *Yellow Sigatoka*, *Cordana*, *Pestalotiopsis*) terhadap fotosintesis dan hasil panen, bagaimana MusaVision hadir sebagai alat bantu skrining dini yang ringan, disertai tombol sekunder menuju `/katalog-patogen`.

### Section 5: Interactive Detection Workspace (`#deteksi` — Inti Aplikasi)
Tata letak 2 kolom bersih di desktop (kiri: Panel Input, kanan: Panel Hasil) dan 1 kolom mengalir rapi di perangkat mobile/tablet.

#### A. Panel Input
1. **Dropzone & Kamera Lapangan:**
   - Area *drag-and-drop* unggah gambar modern + tombol khusus **"Ambil Foto Kamera"** (`accept="image/*" capture="environment"`).
   - Pratinjau foto sebelum dianalisis + tombol utama **"Analisis Daun Pisang"**.
2. **Galeri 5 Sampel Uji Instan:**
   - Mengambil data dari `GET /api/samples`.
   - **Aturan Filter Wajib di `main.js`:** Saring daftar agar **hanya menampilkan item yang nama filenya diawali `sample_`**. Foto *hero* dan *pillar* di `static/samples/` tidak boleh ikut muncul di galeri uji.
3. **Pengaturan Peneliti Terlipat (*Default Tertutup*):**
   - Dibungkus elemen `<details class="researcher-panel">` dengan `<summary>Pengaturan Lanjutan (Mode Peneliti / Pengujian)</summary>`.
   - Parameter di dalamnya:
     - `use_clahe` (Checkbox, default: `true` / `checked`)
     - `conf_threshold` (Range slider `0.10 - 0.85`, default: `0.25`)
     - `iou_threshold` (Range slider `0.20 - 0.80`, default: `0.45`)

#### B. Panel Output Hasil Analisis
1. **State Loading:** Indikator pemrosesan elegan (*"Memvalidasi citra daun & menganalisis pola bercak..."*).
2. **State Ditolak (`status === "rejected"` atau `"no_detection"`):**
   - Kartu peringatan sopan beraksen terracotta menampilkan `data.title` (seragam **"Objek Bukan Daun Pisang"**) dan `data.reason`.
   - Tidak menampilkan label teknis internal yang membingungkan petani.
3. **State Sukses (`status === "success"`):**
   - **Visual Comparison Viewer:** Tab interaktif untuk berpindah antara **Hasil Deteksi** (`images.annotated_b64`), **CIE-LAB CLAHE** (`images.clahe_b64`), dan **Foto Asli** (`images.original_b64`).
   - **Kartu Diagnosis Utama:** Menampilkan `agronomy.display_name`, nama ilmiah (`agronomy.scientific_name`), lencana tingkat keparahan (`agronomy.severity_category`), jumlah total deteksi (`total_detections`), serta pemisahan hitungan **Tingkat Bercak / Lesion-Level** (`lesion_level_count`) dan **Tingkat Helai Daun / Leaf-Level** (`leaf_level_count`).
   - **Kartu Tindakan Sanitasi & Kode FRAC (Fokus Utama Petani):**
     - Gejala Visual (`agronomy.symptoms`)
     - Protokol Pemangkasan Sanitasi / *Deleafing* (`agronomy.deleafing_protocol`)
     - Rekomendasi Pengendalian & Rotasi Fungisida (`agronomy.frac_recommendation` + deretan badge dari `agronomy.frac_codes`)
     - Kotak Catatan Konsultasi PPL/POPT (`agronomy.ppl_disclaimer`)
   - **Rincian Deteksi Per Kotak:** Tabel/daftar rapi untuk setiap elemen dalam array `detections` (`id`, `class_name`, `confidence_pct`, `box_area_ratio_pct`, `granularity`).
   - **Telemetri Latensi (Ringkas / Collapsible):** Menampilkan `preprocess_ms`, `inference_nms_ms`, `postprocess_ms`, `server_total_ms`, dan `client_roundtrip_ms` (diukur via `performance.now()` di JS).

### Section 6: Smart Farming Solutions — 3 Pilar Tindakan Sanitasi (`#sanitasi`)
- **Judul (Word Reveal):** *"Tindakan Sanitasi & Pengendalian Berkelanjutan."*
- Grid 3 kartu editorial (menggunakan **Motion** untuk animasi masuk bertahap & *hover lift* + *image zoom*):
  1. **Pemangkasan Sanitasi (*Deleafing*) Terukur** — Foto: `/static/samples/pillar_sanitation_deleafing.jpg`. Memangkas bagian helai daun nekrotik dengan pisau bersih sambil mempertahankan minimal 6-8 daun fungsional sehat per pohon.
  2. **Rotasi Fungisida Berstandar Kode FRAC** — Foto: `/static/samples/pillar_frac_spraying.jpg`. Membedakan penggunaan fungisida sistemik kuratif (`FRAC 3` & `FRAC 11`) untuk Sigatoka dan kontak protektif ekonomis (`FRAC M03/M05`) untuk Cordana/Pestalotiopsis guna mencegah resistensi jamur.
  3. **Manajemen Kanopi & Drainase Lahan** — Foto: `/static/samples/pillar_canopy_management.jpg`. Mengatur sirkulasi udara, jarak tanam, dan drainase kebun untuk menekan kelembapan pemicu perkembangan spora patogen.

### Section 7: Editorial Footer
- Latar `#12261C` dengan teks `#F7F6F1`.
- Ringkasan singkat **MusaVision**, navigasi cepat (`Beranda`, `Misi`, `Deteksi AI`, `Sanitasi`, `Katalog Patogen`), dan *disclaimer* bahwa aplikasi merupakan sistem pendukung keputusan skrining dini yang tetap menganjurkan validasi PPL/POPT.

---

## 5. Spesifikasi Arsitektur Animasi & Interaksi

### 5.1 Lenis — Smooth Scroll (Sinkron dengan GSAP)
- **Library CDN:** `https://cdn.jsdelivr.net/npm/lenis@1.1.20/dist/lenis.min.js` (beserta CSS bawaannya bila diperlukan).
- **Konfigurasi:**
  - `duration: 1.15`, `smoothWheel: true`, `touchMultiplier: 1.5`.
  - **Sinkronisasi Wajib:** Hubungkan Lenis ke GSAP `ScrollTrigger` agar posisi pemicu scroll selalu akurat:
    ```javascript
    const lenis = new Lenis({ duration: 1.15, smoothWheel: true });
    lenis.on("scroll", ScrollTrigger.update);
    gsap.ticker.add((time) => {
      lenis.raf(time * 1000);
    });
    gsap.ticker.lagSmoothing(0);
    ```
  - **Anchor Smooth Navigation:** Semua klik tautan `#beranda`, `#misi`, `#deteksi`, `#sanitasi` diarahkan melalui `lenis.scrollTo(targetEl, { offset: -76 })`.
  - **Dynamic Height Refresh:** Setiap kali hasil deteksi muncul di `#deteksi` atau panel `<details>` dibuka/ditutup, panggil `ScrollTrigger.refresh()` agar animasi section `#sanitasi` di bawahnya tidak meleset posisi.

### 5.2 GSAP + ScrollTrigger — Judul Muncul Per Kata (*Word-by-Word Scroll Reveal*)
- **Library CDN:**
  - `https://cdn.jsdelivr.net/npm/gsap@3.12.7/dist/gsap.min.js`
  - `https://cdn.jsdelivr.net/npm/gsap@3.12.7/dist/ScrollTrigger.min.js`
- **Implementasi Bebas Plugin Berbayar (Custom Word Splitter):**
  - Tandai semua judul utama (*Hero*, *Mission*, *Workspace*, *Sanitasi*) dengan atribut `data-reveal="words"`.
  - Buat fungsi helper JS `splitHeadingIntoWords(el)` yang membungkus setiap kata secara aman (menjaga spasi & tag `<br>`/`<em>`) menjadi struktur:
    ```html
    <span class="word-mask"><span class="word-inner">Kata</span></span>
    ```
  - CSS: `.word-mask { display: inline-block; overflow: hidden; vertical-align: bottom; padding-bottom: 0.08em; }` dan `.word-inner { display: inline-block; will-change: transform, opacity; }`.
  - Animasi GSAP:
    - Untuk judul di **Hero** (langsung terlihat saat muat): animasi langsung berjalan tanpa menunggu scroll (`yPercent: 110 -> 0`, `opacity: 0 -> 1`, `duration: 0.8`, `stagger: 0.055`, `ease: "power3.out"`).
    - Untuk judul **Section di bawah fold**: gunakan `ScrollTrigger` (`trigger: el`, `start: "top 85%"`, `once: true`, `yPercent: 110 -> 0`, `opacity: 0 -> 1`, `duration: 0.75`, `stagger: 0.05`, `ease: "power3.out"`).

### 5.3 Motion (`motion.dev`) — Animasi Masuk Card & Hover Micro-Interactions
- **Library CDN (ES Module):**
  `import { animate, inView, stagger, hover } from "https://cdn.jsdelivr.net/npm/motion@11.15.0/+esm";`
- **Animasi Masuk Kartu (*Scroll-Triggered Card Entrance*):**
  - Target: kartu 3 pilar sanitasi (`.pillar-card`), kartu metrik/standar (`.standard-item`), kartu misi (`.mission-card`), serta kartu hasil diagnosis & sanitasi saat respons `/predict` dirender.
  - Gunakan `inView(container, () => { animate(cards, { opacity: [0, 1], y: [28, 0], scale: [0.98, 1] }, { duration: 0.65, delay: stagger(0.09), easing: [0.22, 1, 0.36, 1] }); })`.
- **Animasi Hover Kartu (*Tactile Spring Hover*):**
  - Hanya aktif pada perangkat pointer presisi (`window.matchMedia("(hover: hover)").matches`) agar tidak mengganggu ketukan layar sentuh di HP petani.
  - Gunakan `hover(card, (el) => { ... })` dengan fisika pegas (*spring*): kartu terangkat halus (`y: -6`), bayangan menebal lembut, dan gambar di dalam kartu (`.pillar-card img`) melakukan zoom halus (`scale: 1.05`), lalu kembali mulus ke `y: 0` dan `scale: 1` saat kursor keluar.

### 5.4 Aksesibilitas & Kinerja
- Hormati preferensi sistem `prefers-reduced-motion: reduce`: jika aktif, nonaktifkan Lenis dan tampilkan seluruh kata serta kartu secara langsung (`opacity: 1`, `transform: none`).
- Gunakan properti GPU-accelerated (`transform`, `opacity`) agar *frame rate* stabil di 60 fps.

---

## 6. Kontrak Integrasi API (Tetap Sama dengan `app.py`)

| Endpoint | Method | Payload / Parameter | Perilaku di Frontend (`static/js/main.js`) |
| :--- | :--- | :--- | :--- |
| `/predict` | `POST` | `FormData`: `image`, `conf_threshold`, `iou_threshold`, `use_clahe` | Hitung `client_roundtrip_ms` via `performance.now()`. Tangani status `success`, `rejected`, `no_detection`, dan `error`. Setelah merender kartu hasil, jalankan animasi masuk **Motion** dan panggil `ScrollTrigger.refresh()`. |
| `/api/samples` | `GET` | — | Filter `data.samples` hanya untuk nama file diawali `sample_`. Saat tombol sampel diklik, *fetch* `sample.url` sebagai `Blob` -> buat `File` -> tampilkan pratinjau -> siap/langsung analisis. |
| `/katalog-patogen` | `GET` | — | Navigasi langsung ke halaman katalog patogen yang telah diselaraskan palet warna dan navbarnya. |

---

## 7. Kriteria Penerimaan (*Acceptance Criteria*)

- [ ] File `app.py` tidak berubah satu baris pun dan seluruh validasi Gatekeeper + YOLO26 Nano + CIE-LAB CLAHE berjalan normal.
- [ ] Tidak ada bagian *testimonial* di seluruh halaman.
- [ ] Lenis *smooth scroll* aktif mulus dan terhubung dengan GSAP `ScrollTrigger` tanpa loncatan (*jitter*).
- [ ] Seluruh judul utama muncul halus kata demi kata saat di-*scroll* dengan GSAP + ScrollTrigger.
- [ ] Seluruh kartu (3 pilar sanitasi, kartu misi, kartu sampel, dan kartu hasil analisis) memiliki animasi masuk dan *hover* responsif berbasis **Motion**.
- [ ] Menu **"Pengaturan Lanjutan (Mode Peneliti / Pengujian)"** tertutup secara bawaan saat halaman pertama dibuka.
- [ ] Galeri sampel uji instan hanya menampilkan 5 foto `sample_*.jpg` (tidak menampilkan foto hero maupun foto pilar).
- [ ] Seluruh foto lokal dari `static/samples/` termuat tanpa tautan rusak dan tampil responsif di desktop maupun smartphone.

---

## 8. Prompt Eksekusi Siap Salin untuk AntiGravity

> Baca dan ikuti dokumen **`PRD_MusaVision_Redesign.md`** secara penuh untuk melakukan redesign frontend MusaVision (`templates/index.html`, `static/css/style.css`, `static/js/main.js`, serta penyelarasan gaya pada `templates/katalog_patogen.html`).
>
> **Aturan Keras:**
> 1. **JANGAN SENTUH `app.py`** dalam bentuk apa pun. Pertahankan kontrak API `/predict`, `/api/samples`, `/sample-file/...`, dan `/katalog-patogen` 100% sesuai `app.py` saat ini.
> 2. **HAPUS TOTAL** bagian testimonial.
> 3. Gunakan gambar referensi Agrovia (jika saya lampirkan screenshot-nya) **HANYA** sebagai acuan tata letak, hierarki tipografi, dan nuansa warna editorial—**JANGAN** gunakan foto atau teks Agrovia; gunakan 100% aset foto lokal milik saya di `/static/samples/` (`musavision_hero_bg.jpg`, `pillar_sanitation_deleafing.jpg`, `pillar_frac_spraying.jpg`, `pillar_canopy_management.jpg`) dan filter `/api/samples` di JS hanya untuk file berawalan `sample_`.
> 4. Terapkan ketiga library animasi sesuai Section 5 PRD:
>    - **Lenis** untuk smooth scroll yang tersinkronisasi dengan `gsap.ticker` dan `ScrollTrigger.update`, plus `ScrollTrigger.refresh()` saat hasil deteksi muncul atau `<details>` dibuka/ditutup.
>    - **GSAP + ScrollTrigger** dengan custom word splitter agar setiap judul (`data-reveal="words"`) muncul halus per kata saat di-scroll.
>    - **Motion (`motion.dev` ESM CDN)** untuk animasi masuk kartu (`inView` + `stagger`) dan *spring hover* pada kartu pilar sanitasi, sampel, serta kartu hasil analisis.
> 5. Pastikan pengaturan `use_clahe`, `conf_threshold`, dan `iou_threshold` terlipat rapi di dalam `<details>` (tertutup secara default) agar antarmuka tetap sederhana bagi petani.