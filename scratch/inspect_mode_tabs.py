with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
m = re.search(r'<!-- Tab Navigasi 4 Mode Ruang Kerja.*?<div class="workspace-canvas-frame">', html, re.DOTALL)
if m:
    print('--- Mode Tabs HTML ---')
    print(m.group(0))

with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

for m in re.finditer(r'\.mode-tab[^{]*\{[^}]*\}', css):
    print(m.group(0))
