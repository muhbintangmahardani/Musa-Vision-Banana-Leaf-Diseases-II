with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

import re
matches = re.finditer(r'(\.faq-[^{]*\{[^}]*\})', css)
for m in matches:
    print(m.group(0))
    print('-'*40)
