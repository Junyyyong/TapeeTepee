import json, re

with open('presets.json', 'r') as f:
    presets = json.load(f)

for i, p in enumerate(presets):
    print(f"Pose {i}")
    for j, shape in enumerate(p):
        fill = re.search(r'fill: (#[0-9a-fA-F]+)', shape).group(1)
        print(f"  Shape {j}: {fill}")
