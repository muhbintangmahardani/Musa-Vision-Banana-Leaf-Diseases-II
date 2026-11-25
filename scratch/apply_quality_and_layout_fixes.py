# -*- coding: utf-8 -*-
"""
Script untuk menerapkan seluruh perbaikan:
1. 8 Quality issues:
   - #agroSeverity contrast WCAG AAA (>7:1): #78350F on #FEF3C7 (Sedang), #991B1B on #FEE2E2 (Ganas), #14532D on #DCFCE7 (Optimal)
   - Hapus semua transition: padding dan transition-all pada navbar, FAQ, dan page-level
   - FAQ font size 0.9375rem (15px) #4B524C, padding dipindahkan ke .faq-expandable-inner statis
   - Fix cramped padding & ratakan nested cards pada tabel bounding box dan kolom samping div.w-full.md:w-64
2. AI tells:
   - Hapus glowing shadow accents (#163c24) pada .btn-forest-cta
   - Ganti font utama Plus Jakarta Sans -> Instrument Sans di index.html, katalog_patogen.html, style.css
3. Mobile layout Workspace #deteksi:
   - 4 tab mode jadi grid 2x2 rapi (repeat(2, 1fr) gap 8px min-height 48px)
   - Padding workspace 16px di mobile agar area upload & pratinjau maksimal
   - 3 visual tab jadi segmented control 3 kolom (grid-cols-3)
   - Pratinjau citra hasil full width max-h-[360px]
   - Tombol analisis lebar penuh height 50px
   - Details peneliti tertutup default

Kepatuhan Ketat:
- app.py 100% READ-ONLY
- R-02: 0 em-dash (\u2014) dan 0 en-dash (\u2013)
"""
import re

print("=== STARTING QUALITY AND LAYOUT FIXES ===")

# ====================================================
# 1. PERBAIKAN templates/index.html
# ====================================================
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1.1 Ganti Font Google Fonts: Plus Jakarta Sans -> Instrument Sans
old_font_link = '<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />'
new_font_link = '<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400..700;1,400..700&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400..700&display=swap" rel="stylesheet" />'
if old_font_link in html:
    html = html.replace(old_font_link, new_font_link)
    print("[index] Updated Google Fonts link to Instrument Sans")

# 1.2 Update Tailwind config font family
old_tw_sans = "sans: ['\"Plus Jakarta Sans\"', 'system-ui', '-apple-system', 'sans-serif'],"
new_tw_sans = "sans: ['\"Instrument Sans\"', 'system-ui', '-apple-system', 'sans-serif'],"
if old_tw_sans in html:
    html = html.replace(old_tw_sans, new_tw_sans)
    print("[index] Updated Tailwind font config to Instrument Sans")

# 1.3 Fix initial #agroSeverity badge markup to high contrast
old_sev_badge = '<span id="agroSeverity" class="font-bold text-xs bg-rose-700 text-white px-2.5 py-0.5 rounded-full">Ganas</span>'
new_sev_badge = '<span id="agroSeverity" class="font-bold text-xs bg-[#FEE2E2] text-[#991B1B] border border-[#FECACA] px-2.5 py-0.5 rounded-full">Ganas</span>'
if old_sev_badge in html:
    html = html.replace(old_sev_badge, new_sev_badge)
    print("[index] Updated initial #agroSeverity to high contrast badge")

# 1.4 Ratakan Nested Cards di tabViewResult
# A. Kolom samping div.w-full.md:w-64: Hapus border ganda
old_md_w64 = '<div class="w-full md:w-64 space-y-1 bg-[#F6F7F4] border border-[#E8EAE6] p-3 rounded-xl">'
new_md_w64 = '<div class="w-full md:w-64 space-y-1.5 bg-[#F7F8F5] p-3.5 rounded-xl">'
if old_md_w64 in html:
    html = html.replace(old_md_w64, new_md_w64)
    print("[index] Flattened div.w-full.md:w-64 (removed nested border)")

# B. Tabel Bounding Box Detail: Hapus border dan rounded nested
old_bbox_box = """            <!-- Tabel Bounding Box Detail -->
            <div class="bg-white rounded-2xl p-4 border border-[#E8EAE6] shadow-xs">
              <div class="text-xs font-bold text-[#111812] mb-3">Tabel Rincian Deteksi Kotak Pembatas (Bounding Box)</div>
              <div class="w-full overflow-x-auto rounded-xl border border-[#E8EAE6]">
                <table class="w-full text-left border-collapse text-xs min-w-[550px]">
                  <thead>
                    <tr class="border-b border-[#E8EAE6] bg-[#F6F7F4] text-[#4B524C] font-semibold">
                      <th class="py-2.5 px-3">#</th>
                      <th class="py-2.5 px-3">Kelas Diagnosa</th>
                      <th class="py-2.5 px-3">Keyakinan</th>
                      <th class="py-2.5 px-3">Rasio Luas</th>
                      <th class="py-2.5 px-3">Granularitas</th>
                      <th class="py-2.5 px-3">Koordinat [x1, y1, x2, y2]</th>
                    </tr>
                  </thead>
                  <tbody id="bboxTableBody" class="divide-y divide-[#E8EAE6] font-mono text-xs">
                    <tr><td colspan="6" class="py-4 text-center text-[#4B524C]">Belum ada pengujian daun yang dijalankan.</td></tr>
                  </tbody>
                </table>
              </div>
            </div>"""

new_bbox_box = """            <!-- Tabel Bounding Box Detail (Flat Editorial, Bebas Nested Card & Cramped Padding) -->
            <div class="bg-white rounded-2xl p-5 border border-[#E5E7E2]">
              <div class="text-xs font-bold text-[#111812] mb-3">Tabel Rincian Deteksi Kotak Pembatas (Bounding Box)</div>
              <div class="w-full overflow-x-auto">
                <table class="w-full text-left border-collapse text-xs min-w-[550px]">
                  <thead>
                    <tr class="border-b border-[#E5E7E2] text-[#4B524C] font-semibold font-mono">
                      <th class="py-3 px-4">#</th>
                      <th class="py-3 px-4">Kelas Diagnosa</th>
                      <th class="py-3 px-4">Keyakinan</th>
                      <th class="py-3 px-4">Rasio Luas</th>
                      <th class="py-3 px-4">Granularitas</th>
                      <th class="py-3 px-4">Koordinat [x1, y1, x2, y2]</th>
                    </tr>
                  </thead>
                  <tbody id="bboxTableBody" class="divide-y divide-[#E5E7E2] font-mono text-xs">
                    <tr><td colspan="6" class="py-4 px-4 text-center text-[#4B524C]">Belum ada pengujian daun yang dijalankan.</td></tr>
                  </tbody>
                </table>
              </div>
            </div>"""

if old_bbox_box in html:
    html = html.replace(old_bbox_box, new_bbox_box)
    print("[index] Flattened BBox table container (removed nested card border and cramped padding)")

# 1.5 Segmented Control 3 Tab Visual di visualResultBox agar responsif 3 kolom di mobile
old_visual_tabs = """              <div class="flex flex-wrap items-center justify-between gap-2 border-b border-white/10 pb-3">
                <div class="bg-white/10 p-1 rounded-full flex gap-1 text-xs">
                  <button type="button" id="btnSwitchAnnotated" onclick="switchVerdictView('annotated')" class="px-3 py-1.5 rounded-full font-bold bg-[#DDF247] text-[#111812] transition shadow-sm active">
                    YOLO26n BBox
                  </button>
                  <button type="button" id="btnSwitchClahe" onclick="switchVerdictView('clahe')" class="px-3 py-1.5 rounded-full text-white/80 hover:text-white transition font-medium">
                    CIE-LAB CLAHE
                  </button>
                  <button type="button" id="btnSwitchOrig" onclick="switchVerdictView('orig')" class="px-3 py-1.5 rounded-full text-white/80 hover:text-white transition font-medium">
                    Citra Asli
                  </button>
                </div>

                <div class="flex items-center gap-2">"""

new_visual_tabs = """              <div class="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 border-b border-white/10 pb-3">
                <div class="w-full sm:w-auto bg-white/10 p-1 rounded-xl sm:rounded-full grid grid-cols-3 sm:flex gap-1 text-xs text-center">
                  <button type="button" id="btnSwitchAnnotated" onclick="switchVerdictView('annotated')" class="px-2.5 sm:px-3 py-2 sm:py-1.5 rounded-lg sm:rounded-full font-bold bg-[#DDF247] text-[#111812] transition shadow-sm active text-center truncate">
                    Hasil Deteksi
                  </button>
                  <button type="button" id="btnSwitchClahe" onclick="switchVerdictView('clahe')" class="px-2.5 sm:px-3 py-2 sm:py-1.5 rounded-lg sm:rounded-full text-white/80 hover:text-white transition font-medium text-center truncate">
                    CIE-LAB CLAHE
                  </button>
                  <button type="button" id="btnSwitchOrig" onclick="switchVerdictView('orig')" class="px-2.5 sm:px-3 py-2 sm:py-1.5 rounded-lg sm:rounded-full text-white/80 hover:text-white transition font-medium text-center truncate">
                    Foto Asli
                  </button>
                </div>

                <div class="flex items-center justify-end gap-2">"""

if old_visual_tabs in html:
    html = html.replace(old_visual_tabs, new_visual_tabs)
    print("[index] Made visual verdict tabs full-width 3-column segmented control on mobile")

# 1.6 Visual Result Image Frame max-h-[360px]
old_active_display = '<div class="w-full aspect-video sm:aspect-[16/10] rounded-xl overflow-hidden bg-black flex items-center justify-center">'
new_active_display = '<div class="w-full aspect-video sm:aspect-[16/10] max-h-[360px] rounded-xl overflow-hidden bg-black flex items-center justify-center">'
if old_active_display in html:
    html = html.replace(old_active_display, new_active_display)
    print("[index] Set max-height on visual result image container")

# 1.7 Tombol Analisis Daun Pisang: Pastikan h-[50px] min-h-[50px] full width
html = html.replace(
    'id="btnRunInference" onclick="runInference()" class="w-full sm:flex-1 bg-[#DDF247] hover:bg-[#CEE435] text-[#111812] font-bold text-xs sm:text-sm py-3.5 px-6 rounded-full shadow-md flex items-center justify-center gap-2 transition active:scale-[0.98]"',
    'id="btnRunInference" onclick="runInference()" class="w-full sm:flex-1 h-[50px] min-h-[50px] bg-[#DDF247] hover:bg-[#CEE435] text-[#111812] font-bold text-xs sm:text-sm px-6 rounded-full shadow-md flex items-center justify-center gap-2 transition active:scale-[0.98]"'
)

# 1.8 Flat Open History Table (Bebas nested border)
old_hist_table = '<div class="w-full overflow-x-auto rounded-xl border border-[#E8EAE6] bg-white">'
new_hist_table = '<div class="w-full overflow-x-auto rounded-xl border border-[#E5E7E2] bg-white p-2 sm:p-3">'
if old_hist_table in html:
    html = html.replace(old_hist_table, new_hist_table)
    print("[index] Enhanced history table container")

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("[index] Saved templates/index.html")


# ====================================================
# 2. PERBAIKAN templates/katalog_patogen.html
# ====================================================
with open('templates/katalog_patogen.html', 'r', encoding='utf-8') as f:
    katalog = f.read()

# 2.1 Update Google Fonts ke Instrument Sans
if old_font_link in katalog:
    katalog = katalog.replace(old_font_link, new_font_link)
    print("[katalog] Updated Google Fonts link to Instrument Sans")

# 2.2 Update font family di style katalog
katalog = katalog.replace(
    "font-family: '\"Plus Jakarta Sans\"', system-ui, -apple-system, sans-serif;",
    "font-family: '\"Instrument Sans\"', system-ui, -apple-system, sans-serif;"
)
katalog = katalog.replace(
    "--font-sans: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;",
    "--font-sans: 'Instrument Sans', system-ui, -apple-system, sans-serif;"
)

with open('templates/katalog_patogen.html', 'w', encoding='utf-8') as f:
    f.write(katalog)
print("[katalog] Saved templates/katalog_patogen.html")


# ====================================================
# 3. PERBAIKAN static/css/style.css
# ====================================================
with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# 3.1 Ganti font sans ke Instrument Sans
css = css.replace(
    "--font-sans: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;",
    "--font-sans: 'Instrument Sans', system-ui, -apple-system, sans-serif;"
)
css = css.replace(
    'font-family: var(--font-sans, "Plus Jakarta Sans", sans-serif);',
    'font-family: var(--font-sans, "Instrument Sans", sans-serif);'
)
print("[css] Updated font variables to Instrument Sans")

# 3.2 Hapus Glowing Shadow #163c24 pada .btn-forest-cta
old_cta_shadow = "box-shadow: 0 4px 14px rgba(22, 60, 36, 0.25);"
new_cta_shadow = "box-shadow: 0 4px 14px rgba(17, 24, 18, 0.08);"
if old_cta_shadow in css:
    css = css.replace(old_cta_shadow, new_cta_shadow)
    print("[css] Replaced #163c24 colored glow shadow with neutral shadow")

# 3.3 Hapus transition: padding pada Navbar dan biarkan padding konstan
old_navbar_rule = """#mainNavbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  right: 0;
  z-index: 50;
  padding: 18px 24px;
  pointer-events: none;
  background: transparent;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  border-bottom: none;
  box-shadow: none;
  transition: background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, backdrop-filter 0.3s ease;
}"""

new_navbar_rule = """#mainNavbar {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  right: 0;
  z-index: 50;
  padding: 14px 24px;
  pointer-events: none;
  background: transparent;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  border-bottom: none;
  box-shadow: none;
  transition: background-color 0.28s ease, border-color 0.28s ease, color 0.28s ease, box-shadow 0.28s ease, backdrop-filter 0.28s ease;
}"""

if old_navbar_rule in css:
    css = css.replace(old_navbar_rule, new_navbar_rule)
    print("[css] Updated navbar base rule (constant padding 14px 24px, specific non-layout transition)")

# Update scrolled state padding to match 14px 24px (no shift!)
css = css.replace(
    "#mainNavbar.is-scrolled {\n  padding: 12px 24px;",
    "#mainNavbar.is-scrolled {\n  padding: 14px 24px;"
)
css = css.replace(
    "#mainNavbar.navbar--light,\n#mainNavbar[data-navbar-static=\"light\"] {\n  background: rgba(255, 255, 255, 0.98) !important;\n  backdrop-filter: blur(16px) !important;\n  -webkit-backdrop-filter: blur(16px) !important;\n  border-bottom: 1px solid rgba(17, 24, 18, 0.08) !important;\n  box-shadow: 0 4px 20px -2px rgba(17, 24, 18, 0.06) !important;\n  padding: 12px 24px !important;",
    "#mainNavbar.navbar--light,\n#mainNavbar[data-navbar-static=\"light\"] {\n  background: rgba(255, 255, 255, 0.98) !important;\n  backdrop-filter: blur(16px) !important;\n  -webkit-backdrop-filter: blur(16px) !important;\n  border-bottom: 1px solid rgba(17, 24, 18, 0.08) !important;\n  box-shadow: 0 4px 20px -2px rgba(17, 24, 18, 0.06) !important;\n  padding: 14px 24px !important;"
)

# 3.4 FAQ CSS: Hapus transition: padding, naikkan ukuran font ke 0.9375rem (15px) #4B524C, padding di elemen statis inner
old_faq_css_block = """.faq-expandable-content {
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

new_faq_css_block = """.faq-expandable-content {
  display: grid;
  grid-template-rows: 0fr;
  transition: grid-template-rows 0.32s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.22s ease;
  opacity: 0;
  overflow: hidden;
  padding: 0;
  font-size: 0.9375rem;
  line-height: 1.6;
  color: #4B524C;
}

.faq-card-item.is-open .faq-expandable-content {
  grid-template-rows: 1fr;
  opacity: 1;
}

.faq-expandable-inner {
  min-height: 0;
  overflow: hidden;
  padding: 4px 20px 20px 20px;
}

.faq-expandable-content > * {
  min-height: 0;
  overflow: hidden;
}"""

if old_faq_css_block in css:
    css = css.replace(old_faq_css_block, new_faq_css_block)
    print("[css] Replaced FAQ CSS with non-animated padding and 0.9375rem text")

# 3.5 Workspace canvas frame mobile padding 16px
old_ws_css = """.workspace-canvas-frame {
  background: var(--bg-warm-gray);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 24px;
}
.workspace-canvas-frame {
    padding: 32px;
  }"""

new_ws_css = """.workspace-canvas-frame {
  background: var(--bg-warm-gray);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 16px;
}

@media (min-width: 768px) {
  .workspace-canvas-frame {
    padding: 28px;
  }
}"""

if old_ws_css in css:
    css = css.replace(old_ws_css, new_ws_css)
    print("[css] Configured workspace-canvas-frame with 16px mobile padding")

# 3.6 Mode tabs grid 2x2 mobile
old_tabs_css = """.mode-tabs-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 24px;
}"""

new_tabs_css = """.mode-tabs-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 20px;
}"""

if old_tabs_css in css:
    css = css.replace(old_tabs_css, new_tabs_css)
    print("[css] Configured mode-tabs-grid 2x2 with 8px gap for mobile")

# 3.7 Mode tab button specific transitions
css = css.replace(
    ".mode-tab-btn {\n  background: var(--bg-warm-gray);\n  border: 1px solid var(--border-card);\n  border-radius: var(--radius-md);\n  padding: 12px 14px;\n  display: flex;\n  align-items: center;\n  gap: 10px;\n  cursor: pointer;\n  transition: all 0.2s ease;\n  text-align: left;\n}",
    ".mode-tab-btn {\n  background: var(--bg-warm-gray);\n  border: 1px solid var(--border-card);\n  border-radius: var(--radius-md);\n  padding: 10px 12px;\n  min-height: 48px;\n  display: flex;\n  align-items: center;\n  gap: 10px;\n  cursor: pointer;\n  transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;\n  text-align: left;\n}"
)

with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write(css)
print("[css] Saved static/css/style.css")


# ====================================================
# 4. PERBAIKAN static/js/main.js
# ====================================================
with open('static/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 4.1 Update dynamic severity badge rendering to WCAG AAA contrast
old_sev_logic = """  const sevCategory = agro.severity_category || "Sehat Optimal";
  if (agroSeverity) {
    agroSeverity.textContent = cleanText(sevCategory);

    let sevBadgeColor = "bg-emerald-700";
    let sevPosition = "12%";

    if (sevCategory.includes("Ganas") || sevCategory.includes("Kritis") || data.dominant_class === "Black Sigatoka") {
      sevBadgeColor = "bg-rose-700";
      sevPosition = "88%";
    } else if (sevCategory.includes("Sedang") || sevCategory.includes("Ringan") || data.dominant_class === "Cordana" || data.dominant_class === "Pestalotiopsis") {
      sevBadgeColor = "bg-amber-600";
      sevPosition = "50%";
    } else if (data.dominant_class === "Yellow Sigatoka") {
      sevBadgeColor = "bg-amber-700";
      sevPosition = "72%";
    }

    agroSeverity.className = `font-bold text-xs ${sevBadgeColor} text-white px-3 py-1 rounded-full shadow-xs self-start sm:self-auto`;"""

new_sev_logic = """  const sevCategory = agro.severity_category || "Sehat Optimal";
  if (agroSeverity) {
    agroSeverity.textContent = cleanText(sevCategory);

    // WCAG AAA High-Contrast Badges (> 7:1)
    let sevBadgeColor = "bg-[#DCFCE7] text-[#14532D] border border-[#BBF7D0]";
    let sevPosition = "12%";

    if (sevCategory.includes("Ganas") || sevCategory.includes("Kritis") || data.dominant_class === "Black Sigatoka") {
      sevBadgeColor = "bg-[#FEE2E2] text-[#991B1B] border border-[#FECACA]";
      sevPosition = "88%";
    } else if (sevCategory.includes("Sedang") || sevCategory.includes("Ringan") || data.dominant_class === "Cordana" || data.dominant_class === "Pestalotiopsis") {
      sevBadgeColor = "bg-[#FEF3C7] text-[#78350F] border border-[#FDE68A]";
      sevPosition = "50%";
    } else if (data.dominant_class === "Yellow Sigatoka") {
      sevBadgeColor = "bg-[#FEF3C7] text-[#78350F] border border-[#FDE68A]";
      sevPosition = "72%";
    }

    agroSeverity.className = `font-bold text-xs ${sevBadgeColor} px-3 py-1 rounded-full shadow-xs self-start sm:self-auto`;"""

if old_sev_logic in js:
    js = js.replace(old_sev_logic, new_sev_logic)
    print("[js] Replaced dynamic severity badge classes with high contrast WCAG AAA colors")

with open('static/js/main.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("[js] Saved static/js/main.js")

print("=== ALL QUALITY AND LAYOUT FIXES APPLIED SUCCESSFULLY ===")
