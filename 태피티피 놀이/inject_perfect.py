import json, re

with open('perfect_matrices_v2.json', 'r') as f:
    matrices = json.load(f)

for m in matrices[0]:
    m['x'] = 0.0
    m['y'] = 0.0
    m['r'] = 0
    m['f'] = 1

json_str = "\n  const computedScaledPresets = " + json.dumps(matrices, indent=4) + ";\n"

with open('태피티피_플레이.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Swap computedScaledPresets array with new string
html = re.sub(r'  const computedScaledPresets = \[.*?\n  \];\n', json_str, html, flags=re.DOTALL)

with open('태피티피_플레이.html', 'w', encoding='utf-8') as f:
    f.write(html)
