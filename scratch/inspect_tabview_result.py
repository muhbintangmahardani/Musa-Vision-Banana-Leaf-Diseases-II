with open('templates/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
match = re.search(r'<div id="tabViewResult".*?<!-- VIEW 4', html, re.DOTALL)
if match:
    print('--- tabViewResult HTML ---')
    print(match.group(0))

match_w64 = re.search(r'md:w-64', html)
if match_w64:
    start = max(0, match_w64.start() - 100)
    end = min(len(html), match_w64.end() + 200)
    print('\n--- md:w-64 HTML ---')
    print(html[start:end])
