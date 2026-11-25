with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
serif_count = len(re.findall(r'font-serif', html))
mono_count = len(re.findall(r'font-mono', html))
sans_count = len(re.findall(r'font-sans', html))

print('index.html font class mentions:')
print(f'font-serif: {serif_count}')
print(f'font-mono: {mono_count}')
print(f'font-sans: {sans_count}')
