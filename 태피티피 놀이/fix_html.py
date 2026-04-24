import json, re

with open('perfect_matrices_v2.json', 'r') as f:
    matrices = json.load(f)

for m in matrices[0]:
    m['x'] = 0.0; m['y'] = 0.0; m['r'] = 0; m['f'] = 1

json_str = "  const computedScaledPresets = " + json.dumps(matrices, indent=4) + ";"

with open('태피티피_플레이.html', 'r', encoding='utf-8') as f:
    html = f.read()

# First, find rawSvgPresets definition
raw_match = re.search(r'(const rawSvgPresets = \[.*?\n\];)', html, re.DOTALL)
if not raw_match:
    print("Cannot find rawSvgPresets")
    exit(1)

# Second, find let customPresets = ... and EVERYTHING AFTER it
rest_match = re.search(r'(  let customPresets =.*)', html, re.DOTALL)
if not rest_match:
    print("Cannot find customPresets block")
    exit(1)

# Extract everything BEFORE <script>
before_script = html[:html.index('<script>') + 8]

# Rebuild the HTML content cleanly!
new_html = before_script + '\n' + raw_match.group(1) + '\n\n' + json_str + '\n\n' + rest_match.group(1)

new_html = new_html.replace('v8', 'v9')

with open('태피티피_플레이.html', 'w', encoding='utf-8') as f:
    f.write(new_html)
