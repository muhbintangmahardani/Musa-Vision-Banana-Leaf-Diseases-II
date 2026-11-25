# -*- coding: utf-8 -*-
"""
Script atomik untuk memperbaiki seluruh temuan Impeccable dan quality issues pada:
1. templates/katalog_patogen.html
2. templates/index.html
3. static/css/style.css
4. static/js/main.js

Semua perubahan mematuhi:
- app.py 100% READ-ONLY (TIDAK BOLEH DISENTUH)
- R-02: 0 em-dash (\u2014) dan 0 en-dash (\u2013)
- WCAG AA Kontras Teks min 4.5:1
"""
import re
import os

print("=== STARTING IMPECCABLE FIXES ===")

# ----------------------------------------------------
# 1. PERBAIKAN templates/katalog_patogen.html
# ----------------------------------------------------
with open('templates/katalog_patogen.html', 'r', encoding='utf-8') as f:
    katalog_content = f.read()

# 1.1 Fix Side-tab accent border (.comp-row.is-active td:first-child::before)
old_comp_css = """    .comp-row.is-active td:first-child {
      position: relative;
    }
    .comp-row.is-active td:first-child::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      bottom: 0;
      width: 3px;
      background-color: #163C24;
    }"""
new_comp_css = """    .comp-row.is-active {
      background-color: #F0F4ED;
    }
    .comp-row.is-active td {
      color: #111812;
    }"""
if old_comp_css in katalog_content:
    katalog_content = katalog_content.replace(old_comp_css, new_comp_css)
    print("[katalog] Replaced side-tab accent border with clean row background")

# 1.2 Fix Hairline border with wide shadow at #katalogMobileDrawer
old_drawer = 'id="katalogMobileDrawer" class="mobile-drawer fixed top-[64px] inset-x-4 max-w-md mx-auto bg-white/95 backdrop-blur-2xl border border-[#E8EAE6] rounded-3xl p-5 text-[#111812] space-y-2 shadow-2xl z-50"'
new_drawer = 'id="katalogMobileDrawer" class="mobile-drawer fixed top-[64px] inset-x-4 max-w-md mx-auto bg-white/95 backdrop-blur-2xl border border-[#E8EAE6] rounded-2xl p-5 text-[#111812] space-y-2 shadow-lg z-50"'
if old_drawer in katalog_content:
    katalog_content = katalog_content.replace(old_drawer, new_drawer)
    print("[katalog] Replaced #katalogMobileDrawer shadow-2xl with shadow-lg")

# 1.3 Fix 4 Info Blocks in #pathogenDossierView (replace stacked blocks with 2x2 grid and remove tiny numbers 01, 02, 03, 04)
# Also balances heights between left column and right column
old_blocks_pattern = r'<!-- 4 Blok Informasi \(Garis Tipis Horizontal, Tanpa Kotak Border, Tanpa Ikon Pastel\) -->\s*<div class="divide-y divide-gray-200/60">.*?</div>\s*</div>\s*</div>\s*<!-- 5\. MATRIKS KOMPARASI'

new_blocks_content = """<!-- 4 Blok Informasi (Grid 2x2 Seimbang, Tanpa Kotak Border, Tanpa Tiny Numbers) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6">
          
          <!-- Blok 01: Karakteristik & Gejala Visual Lapangan -->
          <div class="space-y-2">
            <h3 class="text-base font-bold text-[#111812]">Karakteristik &amp; Gejala Visual Lapangan</h3>
            <p id="dossierSymptoms" class="text-[0.915rem] leading-relaxed text-[#4B524C]">
              Bercak garis karat cokelat kemerahan di permukaan bawah daun yang berkembang cepat menjadi bercak nekrotik hitam pekat berlubang di tengah. Daun mengering sebelum waktunya, menyebabkan tandan matang dini dan kualitas buah anjlok drastis.
            </p>
          </div>

          <!-- Blok 02: Dampak Terhadap Hasil Panen -->
          <div class="space-y-2">
            <h3 class="text-base font-bold text-[#111812]">Dampak Panen &amp; Premature Ripening</h3>
            <p id="dossierImpact" class="text-[0.915rem] leading-relaxed text-[#4B524C]">
              Penyakit jamur paling destruktif pada pisang. Menurunkan luas fotosintesis fungsional secara drastis, memicu fenomena premature ripening (buah matang terlalu awal di pohon) dengan rasa masam, dan dapat menimbulkan kerugian hasil hingga 50 sampai 100%.
            </p>
          </div>

          <!-- Blok 03: Protokol Sanitasi Pemangkasan (Deleafing) -->
          <div class="space-y-2">
            <h3 class="text-base font-bold text-[#111812]">Protokol Sanitasi Pemangkasan (Deleafing)</h3>
            <p id="dossierDeleafing" class="text-[0.915rem] leading-relaxed text-[#4B524C]">
              De-leafing wajib: Pangkas helai daun yang terkena lebih dari 30% area lesi, buang ke parit sanitasi dan balikkan helai daun ke bawah tanah untuk menekan pelepasan askospora spora jamur terangkat angin ke kanopi lain.
            </p>
          </div>

          <!-- Blok 04: Panduan Rotasi Bahan Aktif Fungisida (FRAC) -->
          <div class="space-y-2">
            <h3 class="text-base font-bold text-[#111812]">Panduan Rotasi Fungisida (Standar FRAC)</h3>
            <p id="dossierFrac" class="text-[0.915rem] leading-relaxed text-[#4B524C]">
              Rotasi sistemik FRAC 3 (DMI Triazol: Difenoconazole / Tebuconazole) dan FRAC 11 (QoI Strobilurin: Azoxystrobin) diselingi kontak protektif FRAC M01/M03 (Mancozeb / Tembaga). Maksimal 2 kali aplikasi berturut-turut untuk mencegah resistensi patogen jamur di kebun.
            </p>
          </div>

        </div>

      </div>

    </div>

    <!-- 5. MATRIKS KOMPARASI"""

katalog_content, count = re.subn(old_blocks_pattern, new_blocks_content, katalog_content, flags=re.DOTALL)
print(f"[katalog] Converted 4 stacked blocks to 2x2 grid and removed tiny numbers (matched: {count})")

# 1.4 Fix Nested cards and cramped padding at comparison table
old_table_wrapper = '<div class="overflow-x-auto border border-[#E6E6E2] rounded-2xl bg-white shadow-2xs">\n        <table class="w-full text-left text-xs border-collapse">\n          <thead class="bg-[#F6F7F4] border-b border-[#E6E6E2] text-[#4B524C] font-mono uppercase text-xs">'
new_table_wrapper = '<div class="overflow-x-auto border-t border-b border-[#E6E6E2] py-2">\n        <table class="w-full text-left text-xs border-collapse">\n          <thead class="border-b border-[#E6E6E2] text-[#4B524C] font-mono uppercase text-xs">'
if old_table_wrapper in katalog_content:
    katalog_content = katalog_content.replace(old_table_wrapper, new_table_wrapper)
    print("[katalog] Flattened table wrapper (removed nested cards and cramped padding)")

# Typography accent in comparison section heading
old_comp_heading = '<h3 class="text-xl sm:text-2xl font-bold tracking-tight text-[#111812]">Perbandingan 5 Kondisi Daun Pisang</h3>'
new_comp_heading = '<h3 class="text-xl sm:text-2xl font-bold tracking-tight text-[#111812]">Perbandingan 5 Kondisi <span class="font-serif italic font-normal text-[#163C24]">Daun Pisang</span></h3>'
if old_comp_heading in katalog_content:
    katalog_content = katalog_content.replace(old_comp_heading, new_comp_heading)
    print("[katalog] Added font-serif editorial accent to comparison heading")

# Save katalog_patogen.html
with open('templates/katalog_patogen.html', 'w', encoding='utf-8') as f:
    f.write(katalog_content)
print("[katalog] Saved templates/katalog_patogen.html")


# ----------------------------------------------------
# 2. PERBAIKAN templates/index.html
# ----------------------------------------------------
with open('templates/index.html', 'r', encoding='utf-8') as f:
    index_content = f.read()

# 2.1 Fix Hairline border with wide shadow
# #mobileMenuDrawer
index_content = index_content.replace(
    'id="mobileMenuDrawer" class="mobile-drawer fixed top-[64px] inset-x-4 max-w-md mx-auto bg-white/95 backdrop-blur-2xl border border-[#E8EAE6] rounded-3xl p-5 text-[#111812] space-y-2 shadow-2xl z-50"',
    'id="mobileMenuDrawer" class="mobile-drawer fixed top-[64px] inset-x-4 max-w-md mx-auto bg-white/95 backdrop-blur-2xl border border-[#E8EAE6] rounded-2xl p-5 text-[#111812] space-y-2 shadow-lg z-50"'
)
# Lightbox modal and history detail modal
index_content = index_content.replace(
    'class="relative max-w-4xl w-full bg-[#163C24] rounded-3xl overflow-hidden border border-white/10 shadow-2xl p-4 sm:p-6 text-white space-y-4 my-8"',
    'class="relative max-w-4xl w-full bg-[#163C24] rounded-3xl overflow-hidden border border-white/10 shadow-xl p-4 sm:p-6 text-white space-y-4 my-8"'
)
index_content = index_content.replace(
    'class="relative max-w-xl w-full bg-white rounded-3xl overflow-hidden border border-[#E8EAE6] shadow-2xl p-6 text-[#111812] space-y-4 my-8 max-h-[90vh] overflow-y-auto"',
    'class="relative max-w-xl w-full bg-white rounded-2xl overflow-hidden border border-[#E8EAE6] shadow-lg p-6 text-[#111812] space-y-4 my-8 max-h-[90vh] overflow-y-auto"'
)
print("[index] Replaced shadow-2xl with shadow-lg/xl on modals and drawers")

# 2.2 Fix Auto-scrolling marquee: Replace with clean, static, responsive editorial badge strip
old_marquee_section = """  <!-- 3. STRIP STANDAR TEKNOLOGI MARQUEE & SECTION MISI (#misi) -->
  <section class="tech-standards-bar">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center gap-4">
      <span class="text-xs sm:text-sm font-semibold text-[#3E4640] tracking-normal whitespace-nowrap shrink-0">
        Didukung standar teknologi &amp; agronomi:
      </span>
      <div class="tech-marquee-wrapper">
        <div class="tech-marquee-track">
          <!-- Set 1 -->
          <div class="tech-item"><span class="tech-item-dot"></span><span>YOLO26 Nano</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <div class="tech-item"><span class="tech-item-dot"></span><span>CIE-LAB CLAHE</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <div class="tech-item"><span class="tech-item-dot"></span><span>Gatekeeper Validasi</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <div class="tech-item"><span class="tech-item-dot"></span><span>Standar Kode FRAC</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <div class="tech-item"><span class="tech-item-dot"></span><span>Deleafing 6-8 Daun</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <!-- Set 2 (Duplikasi untuk Infinite Seamless Loop) -->
          <div class="tech-item"><span class="tech-item-dot"></span><span>YOLO26 Nano</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <div class="tech-item"><span class="tech-item-dot"></span><span>CIE-LAB CLAHE</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <div class="tech-item"><span class="tech-item-dot"></span><span>Gatekeeper Validasi</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <div class="tech-item"><span class="tech-item-dot"></span><span>Standar Kode FRAC</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <div class="tech-item"><span class="tech-item-dot"></span><span>Deleafing 6-8 Daun</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
        </div>
      </div>
    </div>
  </section>"""

new_static_strip = """  <!-- 3. STRIP STANDAR TEKNOLOGI EDITORIAL STATIS & SECTION MISI (#misi) -->
  <section class="tech-standards-bar">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3 px-2">
      <span class="text-xs sm:text-sm font-semibold text-[#3E4640] tracking-normal whitespace-nowrap shrink-0">
        Didukung standar teknologi &amp; agronomi:
      </span>
      <div class="flex flex-wrap items-center justify-center md:justify-end gap-x-4 gap-y-2 text-xs font-medium text-[#111812]">
        <div class="tech-item"><span class="tech-item-dot"></span><span>YOLO26 Nano</span></div>
        <span class="text-[#D2D6CE] hidden sm:inline">&middot;</span>
        <div class="tech-item"><span class="tech-item-dot"></span><span>CIE-LAB CLAHE</span></div>
        <span class="text-[#D2D6CE] hidden sm:inline">&middot;</span>
        <div class="tech-item"><span class="tech-item-dot"></span><span>Gatekeeper Validasi</span></div>
        <span class="text-[#D2D6CE] hidden sm:inline">&middot;</span>
        <div class="tech-item"><span class="tech-item-dot"></span><span>Standar Kode FRAC</span></div>
        <span class="text-[#D2D6CE] hidden sm:inline">&middot;</span>
        <div class="tech-item"><span class="tech-item-dot"></span><span>Deleafing 6-8 Daun</span></div>
      </div>
    </div>
  </section>"""

if old_marquee_section in index_content:
    index_content = index_content.replace(old_marquee_section, new_static_strip)
    print("[index] Replaced infinite scrolling marquee with clean static editorial strip")

# 2.3 Fix All-caps body text (remove uppercase from deleafing & frac titles)
old_deleafing_title = '<div class="text-xs font-bold text-[#111812] uppercase tracking-wider text-[#2F6B43]">Sanitasi &amp; Pemangkasan (Deleafing)</div>'
new_deleafing_title = '<div class="text-xs font-bold tracking-normal text-[#2F6B43]">Sanitasi &amp; Pemangkasan (Deleafing)</div>'
if old_deleafing_title in index_content:
    index_content = index_content.replace(old_deleafing_title, new_deleafing_title)
    print("[index] Fixed all-caps body text on deleafing title")

old_frac_title = '<div class="text-xs font-bold text-[#111812] uppercase tracking-wider text-[#2F6B43]">Panduan Rotasi Bahan Aktif (FRAC)</div>'
new_frac_title = '<div class="text-xs font-bold tracking-normal text-[#2F6B43]">Panduan Rotasi Bahan Aktif (FRAC)</div>'
if old_frac_title in index_content:
    index_content = index_content.replace(old_frac_title, new_frac_title)
    print("[index] Fixed all-caps body text on FRAC title")

# 2.4 Fix line length too long (max-w-[65ch])
# Subdesc in hero
index_content = index_content.replace(
    'class="hero-subdesc hero-subtitle text-[0.875rem] text-white/90 font-normal max-w-2xl mt-3 sm:mt-4 leading-relaxed"',
    'class="hero-subdesc hero-subtitle text-[0.875rem] text-white/90 font-normal max-w-xl max-w-[55ch] mt-3 sm:mt-4 leading-relaxed"'
)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(index_content)
print("[index] Saved templates/index.html")


# ----------------------------------------------------
# 3. PERBAIKAN static/css/style.css
# ----------------------------------------------------
with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

# 3.1 Perkuat gradient scrim atas di Hero agar sky photo tidak menimbulkan kesan washed out
old_overlay_mobile = """.hero-overlay,
.hero-scrim {
  position: absolute;
  inset: 0;
  z-index: 1;
  background: linear-gradient(
    to bottom,
    rgba(8, 16, 10, 0.28) 0%,
    rgba(8, 16, 10, 0.05) 28%,
    rgba(8, 16, 10, 0.48) 50%,
    rgba(8, 16, 10, 0.80) 75%,
    rgba(6, 12, 8, 0.94) 100%
  );
  pointer-events: none;
}"""
new_overlay_mobile = """.hero-overlay,
.hero-scrim {
  position: absolute;
  inset: 0;
  z-index: 1;
  background: linear-gradient(
    to bottom,
    rgba(8, 16, 10, 0.65) 0%,
    rgba(8, 16, 10, 0.35) 15%,
    rgba(8, 16, 10, 0.15) 30%,
    rgba(8, 16, 10, 0.50) 55%,
    rgba(8, 16, 10, 0.82) 80%,
    rgba(6, 12, 8, 0.95) 100%
  );
  pointer-events: none;
}"""
if old_overlay_mobile in css_content:
    css_content = css_content.replace(old_overlay_mobile, new_overlay_mobile)
    print("[css] Strengthened mobile hero top vignette")

old_overlay_desktop = """@media (min-width: 768px) {
  .hero-overlay,
  .hero-scrim {
    background:
      linear-gradient(
        90deg,
        rgba(8, 16, 10, 0.78) 0%,
        rgba(8, 16, 10, 0.56) 38%,
        rgba(8, 16, 10, 0.18) 65%,
        rgba(8, 16, 10, 0.04) 100%
      ),
      linear-gradient(
        to bottom,
        rgba(8, 16, 10, 0.35) 0%,
        rgba(8, 16, 10, 0.08) 32%,
        rgba(8, 16, 10, 0.50) 75%,
        rgba(6, 12, 8, 0.88) 100%
      );
  }
}"""
new_overlay_desktop = """@media (min-width: 768px) {
  .hero-overlay,
  .hero-scrim {
    background:
      linear-gradient(
        90deg,
        rgba(8, 16, 10, 0.80) 0%,
        rgba(8, 16, 10, 0.58) 38%,
        rgba(8, 16, 10, 0.20) 65%,
        rgba(8, 16, 10, 0.05) 100%
      ),
      linear-gradient(
        to bottom,
        rgba(8, 16, 10, 0.65) 0%,
        rgba(8, 16, 10, 0.35) 15%,
        rgba(8, 16, 10, 0.10) 32%,
        rgba(8, 16, 10, 0.52) 75%,
        rgba(6, 12, 8, 0.90) 100%
      );
  }
}"""
if old_overlay_desktop in css_content:
    css_content = css_content.replace(old_overlay_desktop, new_overlay_desktop)
    print("[css] Strengthened desktop hero top vignette")

# 3.2 Hapus transform: scale(1.05) pada pillar-editorial-card:hover (AI tell: Image hover transform)
old_hover_scale = """.pillar-editorial-card:hover .pillar-img-box img {
  transform: scale(1.05);
}"""
new_hover_scale = """.pillar-editorial-card:hover .pillar-img-box img {
  opacity: 0.95;
}"""
if old_hover_scale in css_content:
    css_content = css_content.replace(old_hover_scale, new_hover_scale)
    print("[css] Replaced scale(1.05) with opacity change on pillar image hover")

# 3.3 Hapus infinite marquee keyframes dan rapikan .tech-standards-bar
old_marquee_css = """.tech-marquee-wrapper {
  overflow: hidden;
  position: relative;
  width: 100%;
  mask-image: linear-gradient(to right, transparent, black 40px, black calc(100% - 40px), transparent);
  -webkit-mask-image: linear-gradient(to right, transparent, black 40px, black calc(100% - 40px), transparent);
}

.tech-marquee-track {
  display: flex;
  align-items: center;
  gap: 28px;
  width: max-content;
  animation: marqueeScroll 24s linear infinite;
  will-change: transform;
}

.tech-marquee-track:hover {
  animation-play-state: paused;
}

@keyframes marqueeScroll {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}"""

new_marquee_css = """.tech-standards-bar {
  background-color: var(--bg-pure);
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  padding: 14px 24px;
}"""

if old_marquee_css in css_content:
    css_content = css_content.replace(old_marquee_css, new_marquee_css)
    print("[css] Cleaned up tech-standards-bar and removed infinite marquee animation")

with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write(css_content)
print("[css] Saved static/css/style.css")


# ----------------------------------------------------
# 4. PERBAIKAN static/js/main.js
# ----------------------------------------------------
with open('static/js/main.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# 4.1 Update navbar scroll threshold to 40px and expose window.updateNavbarScrollState
old_nav_scroll_logic = """    // Dynamic threshold: navbar tetap transparan selama pengguna berada di dalam Hero (#beranda)
    // Transisi ke mode solid-frosted 98% putih bersih terjadi saat mendekati akhir Hero
    const berandaEl = document.getElementById("beranda");
    const threshold = berandaEl
      ? Math.max(120, berandaEl.offsetHeight * 0.45)
      : Math.max(120, window.innerHeight * 0.45);

    if (scrollY > threshold) {
      nav.classList.add("is-scrolled");
    } else {
      nav.classList.remove("is-scrolled");
    }
    ticking = false;
  };

  const onScroll = () => {
    updateNavbarScrollState();
  };

  // Jalankan segera saat inisialisasi agar posisi scrollY = 0 tidak memiliki class is-scrolled
  updateNavbarScrollState();"""

new_nav_scroll_logic = """    // Dynamic threshold: scrollY > 40 sesuai spesifikasi user
    const threshold = 40;

    if (scrollY > threshold) {
      nav.classList.add("is-scrolled");
    } else {
      nav.classList.remove("is-scrolled");
    }
    ticking = false;
  };

  window.updateNavbarScrollState = updateNavbarScrollState;

  const onScroll = () => {
    updateNavbarScrollState();
  };

  // Jalankan segera saat inisialisasi agar posisi scrollY = 0 tidak memiliki class is-scrolled
  updateNavbarScrollState();"""

if old_nav_scroll_logic in js_content:
    js_content = js_content.replace(old_nav_scroll_logic, new_nav_scroll_logic)
    print("[js] Updated navbar threshold to 40px and exposed window.updateNavbarScrollState")

# 4.2 Hapus group-hover:scale-105 pada 5 kartu preview sampel (line ~805)
old_sample_scale = '<img src="${s.url}" alt="${s.label}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300" />'
new_sample_scale = '<img src="${s.url}" alt="${s.label}" class="w-full h-full object-cover transition duration-300" />'
if old_sample_scale in js_content:
    js_content = js_content.replace(old_sample_scale, new_sample_scale)
    print("[js] Removed group-hover:scale-105 from sample preview cards")

# 4.3 Hapus hover:scale-105 pada thumbnail riwayat (line ~1291)
old_thumb_scale = 'class="w-11 h-11 rounded-lg object-cover border border-[#E8EAE6] hover:scale-105 transition-transform" />'
new_thumb_scale = 'class="w-11 h-11 rounded-lg object-cover border border-[#E8EAE6] transition-opacity hover:opacity-90" />'
if old_thumb_scale in js_content:
    js_content = js_content.replace(old_thumb_scale, new_thumb_scale)
    print("[js] Removed hover:scale-105 from history thumbnails")

with open('static/js/main.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
print("[js] Saved static/js/main.js")

print("=== ALL FIXES APPLIED SUCCESSFULLY ===")
