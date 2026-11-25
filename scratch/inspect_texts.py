import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    idx_content = f.read()

# Find tags containing text-xs
xs_matches = re.findall(r'<([a-zA-Z0-9]+)[^>]*class=[\'"]([^\'"]*text-xs[^\'"]*)[\'"][^>]*>([^<]*)', idx_content)
print(f'Total text-xs in index.html: {len(xs_matches)}')
for tag, cls, txt in xs_matches[:25]:
    txt_clean = txt.strip()
    if txt_clean:
        print(f'  <{tag}> [{cls}]: {txt_clean[:60]}')
