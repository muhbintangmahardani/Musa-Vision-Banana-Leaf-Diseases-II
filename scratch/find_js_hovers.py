import re

with open('static/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Find all occurrences of hover in main.js
matches = re.finditer(r'hover[a-zA-Z0-9_\-:]*', js)
for m in set(m.group(0) for m in matches):
    print(m)
