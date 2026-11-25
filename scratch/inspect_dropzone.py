with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(460, 640):
    print(f'{i+1}: {lines[i]}', end='')
