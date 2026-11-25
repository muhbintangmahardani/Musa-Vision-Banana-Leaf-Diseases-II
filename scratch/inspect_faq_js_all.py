with open('static/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re
print('Searching for faq in main.js:')
for m in re.finditer(r'faq[a-zA-Z0-9_\-]*', js, re.IGNORECASE):
    start = max(0, m.start() - 40)
    end = min(len(js), m.end() + 60)
    print(js[start:end])
    print('-'*40)
