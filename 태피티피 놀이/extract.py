import os, json, math, re
from svgpathtools import parse_path, Line

with open('presets.json', 'r') as f:
    presets = json.load(f)

source_elements = presets[0] # Note: presets[0] was 포즈-기본.svg! It's TINY!

html_path = '태피티피_플레이.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# I need the TRUE original shapes which are huge.
# They are now back in rawSvgPresets[0]!
import ast
m = re.search(r'const rawSvgPresets = (\[\s*\[.*?\])', html, re.DOTALL)
if m:
    parsed_str = m.group(1).replace("'<polygon", '"<polygon').replace("'<path", '"<path').replace("/>',", '/>",').replace("/>'", '/>"')
    # just extract the first array block
    first_list_match = re.search(r'\[\s*("<(?:polygon|path)[^>]+>"(?:\s*,\s*"<(?:polygon|path)[^>]+>")*)\s*\]', m.group(1))
    if first_list_match:
        # replace any weird line breaks
        s = "[" + first_list_match.group(1) + "]"
        true_source_elements = json.loads(s)
    else:
        print("fail parse")
        exit(1)

def get_d_from_element(el_str):
    if "<polygon" in el_str:
        pts_match = re.search(r'points="([^"]+)"', el_str)
        if pts_match:
            pts_str = pts_match.group(1).replace('\r', ' ').replace('\n', ' ').strip()
            pts = [p for p in re.split(r'[, ]+', pts_str) if p]
            if len(pts) >= 4:
                d = "M " + pts[0] + "," + pts[1]
                for i in range(2, len(pts), 2):
                    if i+1 < len(pts):
                        d += " L " + pts[i] + "," + pts[i+1]
                d += " Z"
                return d
    elif "<path" in el_str:
        d_match = re.search(r'd="([^"]+)"', el_str)
        if d_match:
            return d_match.group(1)
    return ""

def sample_path(d_str, num_points=30):
    try:
        p = parse_path(d_str)
        pts = []
        for i in range(num_points):
            if p.length() == 0:
                if len(p)>0 and isinstance(p[0], Line):
                    c = p[0].point(0.5)
                    pts.append((c.real, c.imag))
                continue
            c = p.point(i / float(num_points - 1))
            pts.append((c.real, c.imag))
        return pts
    except:
        return []

def bbox(pts):
    if not pts: return 0,0,0,0
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)

def centroid(pts):
    if not pts: return 0,0
    bx1, by1, bx2, by2 = bbox(pts)
    return bx1 + (bx2-bx1)/2.0, by1 + (by2-by1)/2.0

def transform_pts(pts, dx, dy, r_deg, f, cx, cy):
    rad = math.radians(r_deg)
    cos_r = math.cos(rad)
    sin_r = math.sin(rad)
    res = []
    for x, y in pts:
        _x = cx + (x - cx) * f
        _y = y
        lx = _x - cx
        ly = _y - cy
        rx = cx + lx * cos_r - ly * sin_r
        ry = cy + lx * sin_r + ly * cos_r
        res.append((rx + dx, ry + dy))
    return res

def dist(p1, p2):
    return math.hypot(p1[0]-p2[0], p1[1]-p2[1])

source_clouds = [sample_path(get_d_from_element(s)) for s in true_source_elements]
source_cents = [centroid(pts) for pts in source_clouds]

# Let's find the scale ratio. We know presets[0] maps to true_source_elements.
# Let's just compare bounding box width of the first element.
bx1,by1,bx2,by2 = bbox(source_clouds[0]) # huge symbol
true_w = bx2 - bx1
target_clouds_base = [sample_path(get_d_from_element(t)) for t in presets[0]]
tx1,ty1,tx2,ty2 = bbox(target_clouds_base[0]) # tiny preset
tiny_w = tx2 - tx1
SCALE = true_w / tiny_w
# print("SCALE FACTOR:", SCALE)

all_presets = []
all_presets.append([{"x": 0, "y": 0, "r": 0, "f": 1} for _ in range(7)]) # pose 0 (symbol)

for targets in presets: # over the 9 poses!
    target_clouds = []
    for t in targets:
        d = get_d_from_element(t)
        # upscale target cloud to match source!
        unscaled_pts = sample_path(d) if d else []
        scaled_pts = [(x * SCALE, y * SCALE) for x, y in unscaled_pts]
        target_clouds.append(scaled_pts)
        
    target_cents = [centroid(pts) for pts in target_clouds]
    
    preset_state = []
    used_targets = set()
    for s_idx, s_cloud in enumerate(source_clouds):
        if not s_cloud:
            preset_state.append({'x':0, 'y':0, 'r':0, 'f':1})
            continue
            
        s_cx, s_cy = source_cents[s_idx]
        best_match = None
        best_err = float('inf')
        
        for t_idx, t_cloud in enumerate(target_clouds):
            if not t_cloud or t_idx in used_targets: continue
            
            t_cx, t_cy = target_cents[t_idx]
            dx = t_cx - s_cx
            dy = t_cy - s_cy
            
            for f in [1, -1]:
                for r in range(0, 360, 15):
                    for ox in [-20, -10, 0, 10, 20]:  # wider search for centroid drift due to scaling bounds
                        for oy in [-20, -10, 0, 10, 20]:
                            test_pts = transform_pts(s_cloud, dx+ox, dy+oy, r, f, s_cx, s_cy)
                            err = sum(min(dist(p1, t) for t in t_cloud) for p1 in test_pts) / len(test_pts)
                            if err < best_err:
                                best_err = err
                                best_match = {'x': round(dx+ox, 1), 'y': round(dy+oy, 1), 'r': r, 'f': f, 't_idx': t_idx, 'err': err}
                                
        if best_match and best_match['err'] < 25.0: # relaxed error bound due to scaling
            used_targets.add(best_match['t_idx'])
            preset_state.append({'x': best_match['x'], 'y': best_match['y'], 'r': best_match['r'], 'f': best_match['f']})
        else:
            preset_state.append({'x': 0, 'y': 0, 'r': 0, 'f': 1})
            
    all_presets.append(preset_state)

# write the newly recovered states into computed_presets_v2.json
with open('computed_presets_v2.json', 'w') as f:
    json.dump(all_presets, f)

