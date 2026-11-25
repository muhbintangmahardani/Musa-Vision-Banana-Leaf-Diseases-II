with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

import re
matches = re.finditer(r'rgba\(\s*22\s*,\s*60\s*,\s*36\s*,\s*0\.25\s*\)', css)
for m in matches:
    start = max(0, m.start() - 100)
    end = min(len(css), m.end() + 100)
    print(css[start:end])
    print('='*50)
