import re

for fpath in ['templates/index.html', 'templates/katalog_patogen.html', 'static/js/main.js', 'static/css/style.css']:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    matches = re.findall(r'class="[^"]*(?:hover:[^\s"]*scale|group-hover:[^\s"]*scale|scale-|hover:-translate|group-hover:translate)[^"]*"', content)
    print(fpath, 'matches:', len(matches))
    for m in matches:
        print('  ', m)

    # also search for img tags specifically
    img_tags = re.findall(r'<img[^>]+>', content)
    for tag in img_tags:
        if 'scale' in tag or 'transform' in tag or 'hover' in tag:
            print('  IMG TAG:', tag)
