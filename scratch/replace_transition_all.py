with open('static/css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace transition: all with specific properties in style.css
css = css.replace("transition: all 0.3s ease;", "transition: background-color 0.3s ease, border-color 0.3s ease, color 0.3s ease, box-shadow 0.3s ease;")
css = css.replace("transition: all 0.25s ease;", "transition: background-color 0.25s ease, border-color 0.25s ease, color 0.25s ease, box-shadow 0.25s ease;")
css = css.replace("transition: all 0.2s ease;", "transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;")

with open('static/css/style.css', 'w', encoding='utf-8') as f:
    f.write(css)

print('Replaced all transition: all in style.css with specific properties')
