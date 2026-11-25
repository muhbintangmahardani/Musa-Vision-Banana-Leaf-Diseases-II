with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

import re
print('--- Transitions in style.css containing padding or transition-all ---')
for m in re.finditer(r'transition[^;\}]*[;\}]', css):
    t = m.group(0)
    if 'padding' in t or 'all' in t:
        start = max(0, m.start() - 60)
        end = min(len(css), m.end() + 20)
        print(css[start:end])
        print('-'*50)

print('\n--- Navbar padding in style.css ---')
for m in re.finditer(r'#mainNavbar[^{]*\{[^}]*\}', css):
    print(m.group(0))
