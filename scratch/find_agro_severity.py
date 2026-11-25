with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()
with open('static/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()
with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

import re
print('--- agroSeverity in index.html ---')
for m in re.finditer(r'agroSeverity', html):
    start = max(0, m.start() - 100)
    end = min(len(html), m.end() + 100)
    print(html[start:end])

print('\n--- agroSeverity in main.js ---')
for m in re.finditer(r'agroSeverity', js):
    start = max(0, m.start() - 100)
    end = min(len(js), m.end() + 150)
    print(js[start:end])

print('\n--- agroSeverity in style.css ---')
for m in re.finditer(r'agroSeverity', css):
    start = max(0, m.start() - 100)
    end = min(len(css), m.end() + 100)
    print(css[start:end])
