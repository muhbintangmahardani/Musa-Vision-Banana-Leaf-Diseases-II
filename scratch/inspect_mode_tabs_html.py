with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
match = re.search(r'<div class="[^"]*mode-tabs[^"]*"', html)
if match:
    print('Container tag:', match.group(0))

# inspect the buttons inside
m_full = re.search(r'<div class="[^"]*mode-tabs[^"]*".*?</div>\s*<!-- Kanvas Workspace', html, re.DOTALL)
if m_full:
    print(m_full.group(0))
