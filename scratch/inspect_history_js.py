with open('static/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re
m = re.search(r'function renderHistoryTable\(.*?\n\}', js, re.DOTALL)
if m:
    print('--- renderHistoryTable JS ---')
    print(m.group(0)[:1500])
