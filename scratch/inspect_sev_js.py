with open('static/js/main.js', 'r', encoding='utf-8') as f:
    js = f.read()

import re
match = re.search(r'const sevCategory = agro\.severity_category.*?;', js, re.DOTALL)
if match:
    start = max(0, match.start() - 50)
    end = min(len(js), match.end() + 700)
    print(js[start:end])
