# DESIGN.md: Sistem Desain Editorial MusaVision
**Identitas Brand:** MusaVision (Sistem Deteksi Penyakit Daun Pisang Berbasis Web)  
**Karakter & Mood:** Editorial Agritech Modern (Hangat, Ilmiah, Terpercaya, dan Membumi untuk Petani Kebun)  
**Dial Pengaturan:** ENERGY 2 / RHYTHM 2 / MOTION 2  

---

## 1. Filosofi & Arah Desain (Design Direction)

MusaVision dirancang dengan pendekatan editorial agritech modern. Antarmuka menjembatani kecanggihan visi komputer (YOLO26 Nano + CIE-LAB CLAHE) dengan keterbacaan tinggi di layar smartphone petani saat berada di bawah terik matahari kebun.

Desain ini menolak estetika AI generik (AI slop) seperti gradien ungu kebiruan acak, glassmorphism berlebihan di seluruh elemen, sudut rounded pill seragam pada setiap komponen, serta bayangan melayang yang tidak beralasan. Setiap elemen visual harus memiliki fungsi hierarki yang jelas.

### Prinsip Utama
1. **Kejujuran Data & Aset Asli:** Menggunakan 100% foto lokal nyata dari kebun dan pengujian (`/static/samples/`), tanpa gambar stok acak, tanpa klaim statistik fiktif, dan tanpa bagian testimonial palsu.
2. **Keterbacaan Lapangan (Outdoor Field Readability):** Kontras teks memenuhi standar WCAG AA (minimal 4.5:1 untuk teks biasa dan 3:1 untuk teks besar) di atas kanvas alabaster hangat.
3. **Hierarki Bentuk yang Disengaja:** Radius sudut bervariasi sesuai level komponen, bukan bentuk kapsul seragam. Tombol aksi utama berbentuk pill, kartu berbentuk lengkung nyaman (16px hingga 20px), dan panel teknis terstruktur rapi.
4. **Copywriting Alami & Bebas Em Dash:** Mematuhi aturan R-02 dengan tidak menggunakan karakter em dash pada seluruh teks antarmuka. Pemisahan kalimat menggunakan tanda koma, titik, titik dua, atau tanda kurung.

---

## 2. Palet Warna (Color Tokens)

Palet warna terinspirasi dari kanvas agrikultur alami: tanah subur, daun pisang fungsional sehat, dan aksen peringatan biologis patogen.

```css
:root {
  /* Latar Belakang & Kanvas */
  --bg-canvas: #F7F6F1;        /* Warm Alabaster: latar utama halaman yang teduh di mata */
  --bg-surface: #FFFFFF;       /* Crisp White: kartu workspace dan panel informasi */
  --bg-forest: #12261C;        /* Deep Forest Green: hero overlay, footer, aksen kontras tinggi */
  --bg-forest-soft: #1C382A;   /* Elevated Forest: kontainer kartu di atas latar gelap */

  /* Warna Aksen Fungsional */
  --accent-green: #2F6B43;     /* Organic Botanical Green: tombol CTA utama dan status Fresh */
  --accent-green-hover: #245434;
  --accent-gold: #C88A2E;      /* Harvest Gold: lencana metrik evaluasi dan Yellow Sigatoka */
  --accent-terracotta: #B84A39;/* Alert Terracotta: peringatan Black Sigatoka dan penolakan Gatekeeper */

  /* Tipografi & Garis */
  --text-primary: #14221B;     /* Deep Botanical Charcoal: teks judul dan body kontras tinggi */
  --text-secondary: #4D5E55;   /* Muted Botanical Sage: teks deskripsi, keterangan, dan sub-label */
  --border-subtle: #E5E3DC;    /* Organic Sand Border: garis batas kartu halus dan pemisah tabel */
  --border-focus: #2F6B43;     /* Focus outline aksesibilitas keyboard */
}
```

### Panduan Dosis Warna
- **Warna Dasar Netral (75%):** `--bg-canvas` dan `--bg-surface`.
- **Warna Karakter Brand (20%):** `--bg-forest` dan `--text-primary`.
- **Warna Aksen Fungsional (5%):** `--accent-green` untuk aksi utama, serta `--accent-gold` dan `--accent-terracotta` murni sebagai penanda status agronomi (tidak dijadikan dekorasi latar belakang).

---

## 3. Sistem Tipografi Editorial

Tipografi memadukan display serif yang berwibawa dengan sans-serif modern yang sangat mudah dibaca.

### Font Families
- **Display Serif:** `Instrument Serif` (Google Fonts), italic dan regular. Digunakan untuk headline utama (*Hero*, judul bagian misi, dan judul pilar sanitasi) untuk menciptakan nuansa publikasi agrikultur bereputasi tinggi.
- **Body & UI Sans-Serif:** `Plus Jakarta Sans` (Google Fonts), bobot 400, 500, 600, dan 700. Digunakan untuk instruksi petani, navigasi, form kontrol, dan label diagnosis.
- **Monospace Data:** `JetBrains Mono` (Google Fonts), bobot 500 dan 600. Digunakan eksklusif untuk telemetri inferensi (milidetik), rasio area lesi (%), kode fungisida FRAC, dan koordinat bounding box.

### Skala Tipografi Responsif (Fluid Scale)
- **Hero Display:** `clamp(2.25rem, 5vw + 1rem, 4.25rem)` dengan `line-height: 1.08` dan `letter-spacing: -0.025em`.
- **Section Heading (H2):** `clamp(1.75rem, 3vw + 0.5rem, 2.75rem)` dengan `line-height: 1.15`.
- **Card Heading (H3):** `clamp(1.125rem, 1.5vw + 0.25rem, 1.375rem)` dengan `font-weight: 600`.
- **Body Text:** `1rem` (16px) di desktop, turun ke `0.9375rem` (15px) di layar ponsel dengan `line-height: 1.6`.
- **Caption & Microcopy:** `0.75rem` hingga `0.8125rem` (12px sampai 13px) dengan `line-height: 1.4`.

---

## 4. Grid, Layout & Spacing (Mobile-First)

Kebun pisang menuntut tata letak yang andal saat dioperasikan dengan satu tangan di ponsel.

### Breakpoints Konten
- **Mobile (Base):** `< 640px` (reflow satu kolom penuh, padding horizontal 16px hingga 20px).
- **Tablet:** `640px - 1023px` (grid 2 kolom adaptif, padding horizontal 24px hingga 32px).
- **Desktop:** `>= 1024px` (grid asimetris terstruktur, container maksimal 1152px atau 1280px).

### Aturan Komponen Mobile
1. **Area Sentuh (Tap Targets):** Seluruh tombol, link navigasi, dan input form memiliki tinggi minimum 44px dengan padding sentuh yang lapang.
2. **Workspace Input & Hasil:** 
   - Di mobile: Panel unggah/kamera berada di atas, diikuti hasil diagnosis di bawahnya secara mengalir alami.
   - Di desktop: Menjadi tata letak 2 kolom berdampingan yang seimbang tanpa scroll horizontal.
3. **Pengaturan Mode Peneliti Terlipat:**
   - Parameter lanjutan (`use_clahe`, `conf_threshold`, `iou_threshold`) wajib dibungkus elemen `<details class="researcher-panel">` dan tertutup secara bawaan (*collapsed by default*). Petani hanya melihat tombol unggah, tombol kamera, dan tombol analisis.
4. **Pencegahan Overflow:** Tidak ada elemen yang menggunakan lebar piksel kaku melebihi layar ponsel. Tabel rincian deteksi dan log riwayat dilengkapi pembungkus `overflow-x: auto` dengan scrollbar halus.

---

## 5. Sistem Gerak & Animasi (Motion Architecture)

Animasi diterapkan secara bertujuan untuk mengarahkan fokus mata pengguna dan memperkuat rasa taktil, bukan sebagai distraksi visual.

### A. Lenis Smooth Scroll
- Durasi: `1.15` detik dengan interpolasi roda mouse halus (`smoothWheel: true`).
- Sinkronisasi GSAP: Terhubung langsung ke `ScrollTrigger.update` dan `gsap.ticker` untuk memastikan koordinat trigger selalu akurat tanpa loncatan (jitter).
- Penyegaran Dinamis: Memanggil `ScrollTrigger.refresh()` secara otomatis saat:
  - Panel hasil diagnosis selesai dirender.
  - Panel peneliti `<details>` dibuka atau ditutup.

### B. GSAP Word-by-Word Scroll Reveal
- Target: Semua headline utama bertanda `data-reveal="words"`.
- Mekanisme: Fungsi `splitHeadingIntoWords` memecah teks menjadi pembungkus:
  ```html
  <span class="word-mask"><span class="word-inner">Kata</span></span>
  ```
- Hero Headline: Animasi berjalan langsung saat halaman dimuat (`yPercent: 110` menuju `0`, durasi `0.8s`, stagger `0.055s`, ease `power3.out`).
- Section Headings: Dipicu saat elemen mencapai `top 85%` viewport (`once: true`).

### C. Motion (`motion.dev` ESM) untuk Kartu & Interaksi Taktil
- **Entrance Animation:** Kartu pilar sanitasi, kartu fitur, dan panel diagnosis muncul dengan efek `inView` bertingkat (stagger `0.08s`, durasi `0.6s`, pergeseran `y: [24, 0]`, opacity `[0, 1]`).
- **Tactile Spring Hover:** Khusus pada perangkat dengan kursor presisi (`@media (hover: hover)`):
  - Kartu terangkat lembut (`y: -6px`) dengan bayangan mendalam.
  - Foto di dalam kartu pilar sanitasi membesar perlahan (`scale: 1.04`).
- **Aksesibilitas Prefers-Reduced-Motion:** Jika pengguna mengaktifkan pengurangan gerak di sistem operasi, seluruh animasi transisi dan Lenis dinonaktifkan seketika (tampil statis tanpa delay).

---

## 6. Penyimpanan Riwayat Pengguna (IndexedDB Architecture)

Untuk mendukung pencatatan riwayat pengujian lapangan yang persisten per peramban tanpa membebani memori, MusaVision menggunakan IndexedDB lokal.

- **Nama Basis Data:** `MusaVisionDB`
- **Versi:** `1`
- **Object Store:** `detection_history` (keyPath: `id`, autoIncrement: true)
- **Index:** `timestamp`, `dominant_class`, `severity_category`
- **Skema Catatan:**
  ```javascript
  {
    id: 1,
    timestamp: "2026-11-24T20:15:00.000Z",
    filename: "sample_black_sigatoka.jpg",
    dominant_class: "Black Sigatoka",
    scientific_name: "Pseudocercospora fijiensis",
    severity_category: "Penyakit Jamur Ganas Utama",
    total_detections: 3,
    lesion_level_count: 3,
    leaf_level_count: 0,
    max_confidence_pct: 88.4,
    server_total_ms: 142.5,
    client_roundtrip_ms: 210.0,
    thumbnail_b64: "data:image/jpeg;base64,..."
  }
  ```
- **Fitur Terintegrasi:**
  - Tambah otomatis setiap kali diagnosa sukses.
  - Tampilan tabel log riwayat responsif.
  - Ekspor riwayat ke berkas `.CSV`.
  - Hapus riwayat lokal dengan konfirmasi.
  - Fallback aman ke `localStorage` jika lingkungan peramban memblokir IndexedDB.

---

## 7. Filter Sampel Uji Kebun (5 Sampel Terpilih)

Galeri uji cepat di workspace hanya menampilkan sampel daun pisang relevan:
1. `sample_black_sigatoka.jpg` (Sigatoka Hitam, Kritis/Ganas)
2. `sample_yellow_sigatoka.jpg` (Sigatoka Kuning, Garis Klorosis)
3. `sample_cordana.jpg` (Bercak Daun Cordana, Pola Berlian)
4. `sample_pestalotiopsis.jpg` (Bercak Tepi Pestalotiopsis)
5. `sample_fresh.jpg` (Daun Sehat Optimal)

Semua berkas lain yang dikembalikan oleh endpoint `/api/samples` (seperti foto hero atau pilar sanitasi) wajib difilter keluar di sisi frontend sebelum dirender ke galeri sampel.
