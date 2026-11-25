with open('static/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re
match = re.search(r'function loadSampleGallery\(.*?\n\}', js, re.DOTALL)
if match:
    print('--- loadSampleGallery JS ---')
    print(match.group(0))

match2 = re.search(r'function renderSampleButtons\(.*?\n\}', js, re.DOTALL)
if match2:
    print('--- renderSampleButtons JS ---')
    print(match2.group(0))
