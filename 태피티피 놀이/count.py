import json

with open('presets.json', 'r') as f:
    presets = json.load(f)

for i, p in enumerate(presets):
    print(f"Preset {i}: {len(p)} shapes")
