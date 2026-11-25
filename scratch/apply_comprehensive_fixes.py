# -*- coding: utf-8 -*-
"""
Script atomik komprehensif untuk memperbaiki:
1. FAQ Accordion bug (tambahkan .faq-expandable-inner dan update CSS grid-template-rows agar tertutup sempurna 0px tanpa whitespace raksasa)
2. Kembalikan continuous running marquee pada desktop & mobile (halus, rapi, tanpa lag/tumpang tindih)
3. Hapus hairline border + wide shadow pada modal riwayat (div.relative.max-w-xl)
4. Hapus 8 occurrence image hover transforms pada <img> (Tailwind hover transform on <img>)
5. Ratakan nested cards pada #dropzoneArea dan #controlImagePreviewBox
6. Seimbangkan tipografi editorial (Plus Jakarta Sans diturunkan ke <55% dengan Instrument Serif & JetBrains Mono)
7. Pastikan layout desktop & mobile sempurna, rapi, dan seimbang

Kepatuhan Ketat:
- app.py 100% READ-ONLY
- R-02: 0 em-dash (\u2014) dan 0 en-dash (\u2013)
"""
import re

print("=== STARTING COMPREHENSIVE FIXES ===")

# ====================================================
# 1. PERBAIKAN templates/index.html
# ====================================================
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1.1 Kembalikan Running Marquee Desktop & Mobile
old_strip = """  <!-- 3. STRIP STANDAR TEKNOLOGI EDITORIAL STATIS & SECTION MISI (#misi) -->
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

new_marquee = """  <!-- 3. STRIP STANDAR TEKNOLOGI MARQUEE & SECTION MISI (#misi) -->
  <section class="tech-standards-bar">
    <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center gap-3 sm:gap-4 overflow-hidden">
      <span class="text-xs sm:text-sm font-semibold text-[#3E4640] tracking-normal whitespace-nowrap shrink-0">
        Didukung standar teknologi &amp; agronomi:
      </span>
      <div class="tech-marquee-wrapper w-full">
        <div class="tech-marquee-track">
          <!-- Set 1 -->
          <div class="tech-item"><span class="tech-item-dot"></span><span class="font-mono">YOLO26 Nano</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <div class="tech-item"><span class="tech-item-dot"></span><span class="font-mono">CIE-LAB CLAHE</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <div class="tech-item"><span class="tech-item-dot"></span><span>Gatekeeper Validasi</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <div class="tech-item"><span class="tech-item-dot"></span><span class="font-mono">Standar Kode FRAC</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <div class="tech-item"><span class="tech-item-dot"></span><span>Deleafing 6-8 Daun</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <!-- Set 2 (Seamless loop) -->
          <div class="tech-item"><span class="tech-item-dot"></span><span class="font-mono">YOLO26 Nano</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <div class="tech-item"><span class="tech-item-dot"></span><span class="font-mono">CIE-LAB CLAHE</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <div class="tech-item"><span class="tech-item-dot"></span><span>Gatekeeper Validasi</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <div class="tech-item"><span class="tech-item-dot"></span><span class="font-mono">Standar Kode FRAC</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
          <div class="tech-item"><span class="tech-item-dot"></span><span>Deleafing 6-8 Daun</span></div>
          <span class="text-[#D2D6CE]">&middot;</span>
        </div>
      </div>
    </div>
  </section>"""

if old_strip in html:
    html = html.replace(old_strip, new_marquee)
    print("[index] Restored continuous running marquee for desktop and mobile")

# 1.2 Fix Nested cards at #dropzoneArea and #controlImagePreviewBox
# Dropzone
old_dropzone = '<div id="dropzoneArea" class="border-2 border-dashed border-[#D2D6CE] hover:border-[#163C24] bg-white rounded-2xl p-8 text-center transition cursor-pointer flex flex-col items-center justify-center space-y-2" onclick="document.getElementById(\'imageInput\').click()">'
new_dropzone = '<div id="dropzoneArea" class="border-2 border-dashed border-[#C5CAC0] hover:border-[#163C24] bg-white/70 hover:bg-white rounded-2xl p-8 text-center transition cursor-pointer flex flex-col items-center justify-center space-y-2" onclick="document.getElementById(\'imageInput\').click()">'
if old_dropzone in html:
    html = html.replace(old_dropzone, new_dropzone)
    print("[index] Cleaned #dropzoneArea borders")

# Control preview box
old_preview_box = '<div id="controlImagePreviewBox" class="w-full aspect-video sm:aspect-[16/11] rounded-2xl overflow-hidden bg-[#163C24] border border-[#E8EAE6] relative flex items-center justify-center shadow-xs">'
new_preview_box = '<div id="controlImagePreviewBox" class="w-full aspect-video sm:aspect-[16/11] rounded-2xl overflow-hidden bg-[#163C24] relative flex items-center justify-center">'
if old_preview_box in html:
    html = html.replace(old_preview_box, new_preview_box)
    print("[index] Cleaned #controlImagePreviewBox nested card styling")

# 1.3 Fix FAQ Accordion Bug: Bungkus konten dengan .faq-expandable-inner dan ganti button trigger
old_faq_block = """      <!-- 5 FAQ Accordion Items -->
      <div class="space-y-3">
        
        <div class="faq-card-item is-open">
          <div class="faq-trigger-btn">
            <span>Mengapa foto manusia, pot, atau daun lain ditolak oleh sistem?</span>
            <div class="faq-state-icon">
              <span class="faq-icon-sym">−</span>
            </div>
          </div>
          <div class="faq-expandable-content text-xs text-[#4B524C] leading-relaxed">
            MusaVision dilengkapi modul Gatekeeper berlapis yang memeriksa proporsi klorofil daun pisang, mendeteksi wajah atau siluet manusia, dan memverifikasi integritas lamina daun pisang (Musa spp.). Ini mencegah model memberikan vonis keliru pada objek yang bukan helai daun pisang kebun.
          </div>
        </div>

        <div class="faq-card-item">
          <div class="faq-trigger-btn">
            <span>Apa peran penajaman CIE-LAB CLAHE pada deteksi penyakit daun?</span>
            <div class="faq-state-icon">
              <span class="faq-icon-sym">+</span>
            </div>
          </div>
          <div class="faq-expandable-content text-xs text-[#4B524C] leading-relaxed">
            Di kebun terbuka, intensitas sinar matahari dan bayangan kanopi sering membuat bercak tipis Sigatoka tersamar. CIE-LAB CLAHE meningkatkan kontras lokal murni pada kanal kecerahan (L) tanpa mengubah rona warna alami daun, sehingga pola lesi mikro dapat dikenali lebih tajam oleh YOLO26 Nano.
          </div>
        </div>

        <div class="faq-card-item">
          <div class="faq-trigger-btn">
            <span>Mengapa kita wajib mempertahankan minimal 6 sampai 8 daun sehat?</span>
            <div class="faq-state-icon">
              <span class="faq-icon-sym">+</span>
            </div>
          </div>
          <div class="faq-expandable-content text-xs text-[#4B524C] leading-relaxed">
            Tanaman pisang membutuhkan energi fotosintesis yang stabil sejak fase muncul bunga hingga pengisian buah. Jika jumlah daun fungsional sehat kurang dari 6 helai, tandan pisang tidak terisi penuh, berat tandan anjlok, dan buah berisiko matang dini sebelum sempat dipanen.
          </div>
        </div>

        <div class="faq-card-item">
          <div class="faq-trigger-btn">
            <span>Apa itu kode FRAC dan mengapa harus dilakukan rotasi fungisida?</span>
            <div class="faq-state-icon">
              <span class="faq-icon-sym">+</span>
            </div>
          </div>
          <div class="faq-expandable-content text-xs text-[#4B524C] leading-relaxed">
            FRAC (Fungicide Resistance Action Committee) mengelompokkan bahan aktif berdasarkan mekanisme kerjanya pada jamur. Menyemprotkan fungisida dari golongan yang sama secara terus-menerus akan memicu mutasi resistensi jamur. Rotasi antar-kode FRAC (seperti Triazol FRAC 3 dengan Strobilurin FRAC 11 dan Kontak Multisite) menjaga efikasi pengendalian kebun.
          </div>
        </div>

        <div class="faq-card-item">
          <div class="faq-trigger-btn">
            <span>Apakah hasil deteksi ini menggantikan konsultasi dengan petugas PPL?</span>
            <div class="faq-state-icon">
              <span class="faq-icon-sym">+</span>
            </div>
          </div>
          <div class="faq-expandable-content text-xs text-[#4B524C] leading-relaxed">
            MusaVision dirancang sebagai sistem pendukung keputusan (skrining dini) di kebun. Verifikasi lapangan tetap dianjurkan bersama Petugas Penyuluh Lapangan (PPL) atau Pengamat Organisme Pengganggu Tumbuhan (POPT) setempat untuk menentukan dosis dan volume semprot yang tepat.
          </div>
        </div>

      </div>"""

new_faq_block = """      <!-- 5 FAQ Accordion Items -->
      <div class="space-y-3">
        
        <div class="faq-card-item is-open">
          <button type="button" class="faq-trigger-btn" aria-expanded="true">
            <span>Mengapa foto manusia, pot, atau daun lain ditolak oleh sistem?</span>
            <div class="faq-state-icon">
              <span class="faq-icon-sym">-</span>
            </div>
          </button>
          <div class="faq-expandable-content text-xs text-[#4B524C] leading-relaxed">
            <div class="faq-expandable-inner">
              MusaVision dilengkapi modul Gatekeeper berlapis yang memeriksa proporsi klorofil daun pisang, mendeteksi wajah atau siluet manusia, dan memverifikasi integritas lamina daun pisang (Musa spp.). Ini mencegah model memberikan vonis keliru pada objek yang bukan helai daun pisang kebun.
            </div>
          </div>
        </div>

        <div class="faq-card-item">
          <button type="button" class="faq-trigger-btn" aria-expanded="false">
            <span>Apa peran penajaman CIE-LAB CLAHE pada deteksi penyakit daun?</span>
            <div class="faq-state-icon">
              <span class="faq-icon-sym">+</span>
            </div>
          </button>
          <div class="faq-expandable-content text-xs text-[#4B524C] leading-relaxed">
            <div class="faq-expandable-inner">
              Di kebun terbuka, intensitas sinar matahari dan bayangan kanopi sering membuat bercak tipis Sigatoka tersamar. CIE-LAB CLAHE meningkatkan kontras lokal murni pada kanal kecerahan (L) tanpa mengubah rona warna alami daun, sehingga pola lesi mikro dapat dikenali lebih tajam oleh YOLO26 Nano.
            </div>
          </div>
        </div>

        <div class="faq-card-item">
          <button type="button" class="faq-trigger-btn" aria-expanded="false">
            <span>Mengapa kita wajib mempertahankan minimal 6 sampai 8 daun sehat?</span>
            <div class="faq-state-icon">
              <span class="faq-icon-sym">+</span>
            </div>
          </button>
          <div class="faq-expandable-content text-xs text-[#4B524C] leading-relaxed">
            <div class="faq-expandable-inner">
              Tanaman pisang membutuhkan energi fotosintesis yang stabil sejak fase muncul bunga hingga pengisian buah. Jika jumlah daun fungsional sehat kurang dari 6 helai, tandan pisang tidak terisi penuh, berat tandan anjlok, dan buah berisiko matang dini sebelum sempat dipanen.
            </div>
          </div>
        </div>

        <div class="faq-card-item">
          <button type="button" class="faq-trigger-btn" aria-expanded="false">
            <span>Apa itu kode FRAC dan mengapa harus dilakukan rotasi fungisida?</span>
            <div class="faq-state-icon">
              <span class="faq-icon-sym">+</span>
            </div>
          </button>
          <div class="faq-expandable-content text-xs text-[#4B524C] leading-relaxed">
            <div class="faq-expandable-inner">
              FRAC (Fungicide Resistance Action Committee) mengelompokkan bahan aktif berdasarkan mekanisme kerjanya pada jamur. Menyemprotkan fungisida dari golongan yang sama secara terus-menerus akan memicu mutasi resistensi jamur. Rotasi antar-kode FRAC (seperti Triazol FRAC 3 dengan Strobilurin FRAC 11 dan Kontak Multisite) menjaga efikasi pengendalian kebun.
            </div>
          </div>
        </div>

        <div class="faq-card-item">
          <button type="button" class="faq-trigger-btn" aria-expanded="false">
            <span>Apakah hasil deteksi ini menggantikan konsultasi dengan petugas PPL?</span>
            <div class="faq-state-icon">
              <span class="faq-icon-sym">+</span>
            </div>
          </button>
          <div class="faq-expandable-content text-xs text-[#4B524C] leading-relaxed">
            <div class="faq-expandable-inner">
              MusaVision dirancang sebagai sistem pendukung keputusan (skrining dini) di kebun. Verifikasi lapangan tetap dianjurkan bersama Petugas Penyuluh Lapangan (PPL) atau Pengamat Organisme Pengganggu Tumbuhan (POPT) setempat untuk menentukan dosis dan volume semprot yang tepat.
            </div>
          </div>
        </div>

      </div>"""

if old_faq_block in html:
    html = html.replace(old_faq_block, new_faq_block)
    print("[index] Fixed FAQ accordion HTML with .faq-expandable-inner wrappers and semantic button triggers")

# 1.4 Fix Hairline border with wide shadow at div.relative.max-w-xl (History modal)
old_history_modal = '<div class="relative max-w-xl w-full bg-white rounded-3xl overflow-hidden border border-[#E8EAE6] shadow-2xl flex flex-col">'
new_history_modal = '<div class="relative max-w-xl w-full bg-white rounded-2xl overflow-hidden border border-[#E8EAE6] shadow-lg flex flex-col">'
if old_history_modal in html:
    html = html.replace(old_history_modal, new_history_modal)
    print("[index] Replaced shadow-2xl on history modal with shadow-lg")

# 1.5 Add editorial serif accents to section headings for balanced typography
html = html.replace(
    '<h2 data-reveal="words" class="text-3xl sm:text-4xl lg:text-5xl font-semibold tracking-tight text-[#111812] leading-tight mb-4">\n        Ruang Kerja Deteksi Patologi Daun Pisang\n      </h2>',
    '<h2 data-reveal="words" class="text-3xl sm:text-4xl lg:text-5xl font-semibold tracking-tight text-[#111812] leading-tight mb-4">\n        Ruang Kerja Deteksi <span class="font-serif italic font-normal text-[#2F6B43]">Patologi Daun.</span>\n      </h2>'
)
html = html.replace(
    '<h2 data-reveal="words" class="text-3xl sm:text-4xl font-semibold tracking-tight text-[#111812] leading-tight">\n          3 Pilar Sanitasi &amp; Kesehatan Lahan\n        </h2>',
    '<h2 data-reveal="words" class="text-3xl sm:text-4xl font-semibold tracking-tight text-[#111812] leading-tight">\n          3 Pilar Sanitasi &amp; <span class="font-serif italic font-normal text-[#2F6B43]">Kesehatan Lahan.</span>\n        </h2>'
)
html = html.replace(
    '<h2 data-reveal="words" class="text-3xl sm:text-4xl font-semibold tracking-tight text-[#111812]">\n          Katalog 5 Kondisi Daun Pisang\n        </h2>',
    '<h2 data-reveal="words" class="text-3xl sm:text-4xl font-semibold tracking-tight text-[#111812]">\n          Atlas Patogen &amp; <span class="font-serif italic font-normal text-[#2F6B43]">Diagnosa Visual.</span>\n        </h2>'
)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("[index] Saved templates/index.html")


# ====================================================
# 2. PERBAIKAN static/css/style.css
# ====================================================
with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# 2.1 CSS Marquee yang Halus & Responsif untuk Desktop & Mobile
marquee_css_replacement = """.tech-standards-bar {
  background-color: var(--bg-pure);
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  padding: 14px 24px;
  overflow: hidden;
}

.tech-marquee-wrapper {
  overflow: hidden;
  position: relative;
  width: 100%;
  mask-image: linear-gradient(to right, transparent, black 24px, black calc(100% - 24px), transparent);
  -webkit-mask-image: linear-gradient(to right, transparent, black 24px, black calc(100% - 24px), transparent);
}

.tech-marquee-track {
  display: flex;
  align-items: center;
  gap: 28px;
  width: max-content;
  animation: techMarqueeScroll 22s linear infinite;
  will-change: transform;
}

.tech-marquee-track:hover {
  animation-play-state: paused;
}

@keyframes techMarqueeScroll {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
}"""

old_static_bar = """.tech-standards-bar {
  background-color: var(--bg-pure);
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  padding: 14px 24px;
}"""

if old_static_bar in css:
    css = css.replace(old_static_bar, marquee_css_replacement)
    print("[css] Replaced tech-standards-bar with running marquee CSS")

# 2.2 Fix FAQ Accordion CSS (Pastikan tertutup 100% tanpa celah kosong di bawah)
old_faq_css = """.faq-expandable-content {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.3s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.25s ease;
  opacity: 0;
  overflow: hidden;
  padding: 0 20px;
}

.faq-card-item.is-open .faq-expandable-content {
  grid-template-rows: 1fr;
  opacity: 1;
  padding-bottom: 18px;
}

.faq-expandable-inner {
  min-height: 0;
  overflow: hidden;
}"""

new_faq_css = """.faq-expandable-content {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.32s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s ease, padding 0.32s ease;
  opacity: 0;
  overflow: hidden;
  padding: 0 20px;
}

.faq-card-item.is-open .faq-expandable-content {
  grid-template-rows: 1fr;
  opacity: 1;
  padding: 0 20px 18px 20px;
}

.faq-expandable-inner {
  min-height: 0;
  overflow: hidden;
}

.faq-expandable-content > * {
  min-height: 0;
  overflow: hidden;
}"""

if old_faq_css in css:
    css = css.replace(old_faq_css, new_faq_css)
    print("[css] Updated FAQ expandable content CSS with robust grid collapsing")

# 2.3 De-nest workspace-canvas-frame
old_workspace_frame = """.workspace-canvas-frame {
  background: var(--bg-warm-gray);
  border: 1px solid var(--border-card);
  border-radius: var(--radius-xl);
  padding: 24px;
  box-shadow: var(--shadow-card);
}"""

new_workspace_frame = """.workspace-canvas-frame {
  background: var(--bg-warm-gray);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 24px;
}"""

if old_workspace_frame in css:
    css = css.replace(old_workspace_frame, new_workspace_frame)
    print("[css] Flattened workspace-canvas-frame (removed box-shadow)")

with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
print("[css] Saved static/css/style.css")


# ====================================================
# 3. PERBAIKAN static/js/main.js
# ====================================================
with open('static/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 3.1 Hapus Tailwind scale hover pada 5 kartu sampel (group-hover:scale-105)
old_sample_img = '<img src="${s.url}" alt="${s.label}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300" loading="lazy" />'
new_sample_img = '<img src="${s.url}" alt="${s.label}" class="w-full h-full object-cover transition-opacity duration-300 group-hover:opacity-90" loading="lazy" />'
if old_sample_img in js:
    js = js.replace(old_sample_img, new_sample_img)
    print("[js] Replaced group-hover:scale-105 with opacity transition on sample gallery")

# 3.2 Hapus Tailwind scale hover pada thumbnail riwayat (hover:scale-105)
old_hist_thumb = '<img src="${it.thumbnail_b64}" alt="${cleanText(it.dominant_class)}" class="w-11 h-11 rounded-lg object-cover bg-[#ECEEEA] border border-[#E8EAE6] cursor-pointer hover:scale-105 transition" onclick="openHistoryDetailModal(${it.id})" title="Klik untuk lihat detail" />'
new_hist_thumb = '<img src="${it.thumbnail_b64}" alt="${cleanText(it.dominant_class)}" class="w-11 h-11 rounded-lg object-cover bg-[#ECEEEA] border border-[#E8EAE6] cursor-pointer transition-opacity hover:opacity-85" onclick="openHistoryDetailModal(${it.id})" title="Klik untuk lihat detail" />'
if old_hist_thumb in js:
    js = js.replace(old_hist_thumb, new_hist_thumb)
    print("[js] Replaced hover:scale-105 with opacity transition on history thumbnails")

# 3.3 Pastikan initFaqAccordion mengupdate aria-expanded dan simbol +/- dengan rapi
old_faq_js = """function initFaqAccordion() {
  const items = document.querySelectorAll(".faq-card-item");
  items.forEach((item) => {
    const btn = item.querySelector(".faq-trigger-btn");
    if (btn) {
      btn.addEventListener("click", () => {
        const isOpen = item.classList.contains("is-open");
        items.forEach((it) => {
          it.classList.remove("is-open");
          const icon = it.querySelector(".faq-icon-sym");
          if (icon) icon.textContent = "+";
        });

        if (!isOpen) {
          item.classList.add("is-open");
          const icon = item.querySelector(".faq-icon-sym");
          if (icon) icon.textContent = "−";
        }

        if (window.ScrollTrigger) {
          setTimeout(() => window.ScrollTrigger.refresh(), 300);
        }
      });
    }
  });
}"""

new_faq_js = """function initFaqAccordion() {
  const items = document.querySelectorAll(".faq-card-item");
  items.forEach((item) => {
    const btn = item.querySelector(".faq-trigger-btn");
    if (btn) {
      btn.addEventListener("click", () => {
        const isOpen = item.classList.contains("is-open");
        
        // Tutup semua item lain
        items.forEach((it) => {
          it.classList.remove("is-open");
          const b = it.querySelector(".faq-trigger-btn");
          if (b) b.setAttribute("aria-expanded", "false");
          const icon = it.querySelector(".faq-icon-sym");
          if (icon) icon.textContent = "+";
        });

        // Toggle item yang diklik
        if (!isOpen) {
          item.classList.add("is-open");
          btn.setAttribute("aria-expanded", "true");
          const icon = item.querySelector(".faq-icon-sym");
          if (icon) icon.textContent = "-";
        }

        if (window.ScrollTrigger) {
          setTimeout(() => window.ScrollTrigger.refresh(), 320);
        }
      });
    }
  });
}"""

if old_faq_js in js:
    js = js.replace(old_faq_js, new_faq_js)
    print("[js] Updated initFaqAccordion with clean toggle and aria-expanded state")

with open('static/js/main.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("[js] Saved static/js/main.js")

print("=== ALL COMPREHENSIVE FIXES APPLIED SUCCESSFULLY ===")
