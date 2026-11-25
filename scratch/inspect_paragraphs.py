import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    idx_content = f.read()

paragraphs = re.findall(r'<p[^>]*class=[\'"]([^\'"]*)[\'"][^>]*>([^<]*)', idx_content)
print(f'Total <p> in index.html: {len(paragraphs)}')
for cls, txt in paragraphs:
    if 'text-xs' in cls or 'text-[0.' in cls:
        print(f'  <p class="{cls}">: {txt.strip()[:60]}')

with open('templates/katalog_patogen.html', 'r', encoding='utf-8') as f:
    kat_content = f.read()

paragraphs_kat = re.findall(r'<p[^>]*class=[\'"]([^\'"]*)[\'"][^>]*>([^<]*)', kat_content)
print(f'\nTotal <p> in katalog_patogen.html: {len(paragraphs_kat)}')
for cls, txt in paragraphs_kat:
    if 'text-xs' in cls or 'text-[0.' in cls:
        print(f'  <p class="{cls}">: {txt.strip()[:60]}')
