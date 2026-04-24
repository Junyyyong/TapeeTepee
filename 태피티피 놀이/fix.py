import json

with open('computed_presets.json', 'r') as f:
    presets = json.load(f)

SCALE = 7.171833535974013

scaled_presets = []
for p in presets:
    scaled_p = []
    for item in p:
        scaled_p.append({
            'x': round(item['x'] * SCALE, 2),
            'y': round(item['y'] * SCALE, 2),
            'r': item['r'],
            'f': item['f']
        })
    scaled_presets.append(scaled_p)

with open('태피티피_플레이.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

# Insert computedScaledPresets BEFORE rawSvgPresets
json_str = "\n  const computedScaledPresets = " + json.dumps(scaled_presets, indent=4) + ";\n"

if 'const computedScaledPresets' not in html:
    html = html.replace("    const rawSvgPresets = [", json_str + "\n    const rawSvgPresets = [")

with open('태피티피_플레이.html', 'w', encoding='utf-8') as f:
    f.write(html)
