with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()
with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
print('--- Shadows with 163c24 in style.css ---')
for m in re.finditer(r'[^;\}]*163[cC]24[^;\}]*shadow[^;\}]*[;\}]|[^;\}]*shadow[^;\}]*163[cC]24[^;\}]*[;\}]', css):
    print(m.group(0))

print('--- Shadows with rgba(22, 60, 36 in style.css ---')
for m in re.finditer(r'[^;\}]*rgba\(\s*22\s*,\s*60\s*,\s*36[^;\}]*[;\}]', css):
    print(m.group(0))

print('--- Shadows in html ---')
for m in re.finditer(r'shadow-[^\s\"\']+', html):
    s = m.group(0)
    if '163c24' in s or 'forest' in s:
        print(s)
