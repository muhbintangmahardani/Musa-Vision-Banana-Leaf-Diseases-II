with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
headings = re.findall(r'<h[1-4][^>]*>.*?</h[1-4]>', html, re.DOTALL)
print(f'Total headings: {len(headings)}')
for h in headings:
    print(re.sub(r'\s+', ' ', h.strip())[:120])
