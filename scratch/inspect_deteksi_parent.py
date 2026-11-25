with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(425, 465):
    print(f'{i+1}: {lines[i]}', end='')
