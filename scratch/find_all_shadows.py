with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

import re
matches = re.finditer(r'box-shadow:[^;\}]+[;\}]', css)
for m in matches:
    print(m.group(0))
