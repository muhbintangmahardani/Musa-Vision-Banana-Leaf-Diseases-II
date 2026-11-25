with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
faq_section = re.search(r'<section id="faq-section".*?</section>', html, re.DOTALL)
if faq_section:
    print('--- FAQ Section HTML ---')
    print(faq_section.group(0)[:1500])
    print('...')
    print(faq_section.group(0)[-1000:])

with open('static/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

faq_js = re.search(r'function initFaqAccordion\(.*?\n\}', js, re.DOTALL)
if faq_js:
    print('\n--- FAQ JS ---')
    print(faq_js.group(0))
