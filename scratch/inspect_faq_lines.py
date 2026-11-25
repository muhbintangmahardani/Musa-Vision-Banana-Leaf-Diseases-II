with open('templates/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1155, 1260):
    print(f'{i+1}: {lines[i]}', end='')
