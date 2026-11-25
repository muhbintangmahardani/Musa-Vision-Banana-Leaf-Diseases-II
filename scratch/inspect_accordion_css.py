with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Let's inspect accordion in style.css
import re
for m in re.finditer(r'accordion[^{]*\{[^}]*\}', css):
    print(m.group(0))
    print('-'*40)
