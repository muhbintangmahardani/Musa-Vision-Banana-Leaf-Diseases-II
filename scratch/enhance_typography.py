with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Enhance bottom bar metrics with font-mono
html = html.replace(
    '<div class="hero-bottom-metric-mid">\n            <span>85.34% mAP@50</span>\n          </div>',
    '<div class="hero-bottom-metric-mid font-mono">\n            <span>85.34% mAP@50</span>\n          </div>'
)
html = html.replace(
    '<div class="hero-bottom-metric-right">\n            <span>5 Kelas Patologi</span>\n          </div>',
    '<div class="hero-bottom-metric-right font-mono">\n            <span>5 Kelas Patologi</span>\n          </div>'
)

# Enhance Agro Sci with font-serif italic
html = html.replace(
    '<p id="agroSci" class="text-xs text-[#2F6B43] font-semibold italic mt-1">Pseudocercospora fijiensis</p>',
    '<p id="agroSci" class="text-sm font-serif italic text-[#2F6B43] mt-1">Pseudocercospora fijiensis</p>'
)

# Enhance pillar tags with font-serif italic accents
html = html.replace(
    '<span class="text-xs font-mono text-[#2F6B43] font-semibold uppercase tracking-wider block mb-1">Pilar 1 &middot; Mekanis</span>',
    '<span class="text-xs font-mono text-[#2F6B43] font-semibold uppercase tracking-wider block mb-1">Pilar 1 &middot; <span class="font-serif italic font-normal text-sm lowercase">mekanis</span></span>'
)
html = html.replace(
    '<span class="text-xs font-mono text-[#2F6B43] font-semibold uppercase tracking-wider block mb-1">Pilar 2 &middot; Kimiawi Terukur</span>',
    '<span class="text-xs font-mono text-[#2F6B43] font-semibold uppercase tracking-wider block mb-1">Pilar 2 &middot; <span class="font-serif italic font-normal text-sm lowercase">kimiawi terukur</span></span>'
)
html = html.replace(
    '<span class="text-xs font-mono text-[#2F6B43] font-semibold uppercase tracking-wider block mb-1">Pilar 3 &middot; Kultur Teknis</span>',
    '<span class="text-xs font-mono text-[#2F6B43] font-semibold uppercase tracking-wider block mb-1">Pilar 3 &middot; <span class="font-serif italic font-normal text-sm lowercase">kultur teknis</span></span>'
)

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Applied font typography refinements to templates/index.html')
