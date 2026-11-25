with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
m = re.search(r'<div id="visualResultBox".*?<!-- Ringkasan Diagnosis', html, re.DOTALL)
if m:
    print('--- Visual Result Box HTML ---')
    print(m.group(0))
