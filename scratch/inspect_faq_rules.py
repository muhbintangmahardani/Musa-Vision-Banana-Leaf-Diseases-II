with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

import re
print('Searching for .faq- in style.css:')
for m in re.finditer(r'\.faq-[a-zA-Z0-9_\-]+[^{]*\{[^}]*\}', css):
    print(m.group(0))
    print('='*40)
