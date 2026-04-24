import json, cv2, numpy as np
import svgpathtools

with open('presets.json', 'r') as f:
    presets = json.load(f)

def get_d(s):
    import re
    if 'polygon' in s:
        m = re.search(r'points="([^"]+)"', s)
        pts = m.group(1).replace('\n', ' ').strip().split()
        d = f"M {pts[0]},{pts[1]}"
        for i in range(2, len(pts), 2):
            if i+1 < len(pts): d += f" L {pts[i]},{pts[i+1]}"
        return d + " Z"
    return re.search(r'd="([^"]+)"', s).group(1)

def shape_len(path_d):
    try:
        p = svgpathtools.parse_path(path_d)
        return p.length()
    except:
        return 0

for i, p in enumerate(presets):
    lens = [round(shape_len(get_d(shape)), 1) for shape in p]
    print(f"Pose {i} lengths:", lens)
