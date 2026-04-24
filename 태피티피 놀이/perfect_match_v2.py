import json, math, re
from svgpathtools import parse_path

SCALE = 7.1718335

def get_d(s):
    if 'polygon' in s:
        m = re.search(r'points="([^"]+)"', s)
        pts = m.group(1).replace('\n', ' ').strip().split()
        d = f"M {pts[0]},{pts[1]}"
        for i in range(2, len(pts), 2):
            if i+1 < len(pts): d += f" L {pts[i]},{pts[i+1]}"
        return d + " Z"
    return re.search(r'd="([^"]+)"', s).group(1)

def get_color(s):
    return re.search(r'fill:\s*(#[0-9a-fA-F-]+)', s, re.I).group(1).lower()

def shape_len(path_d):
    try: return parse_path(path_d).length()
    except: return 0

# Sample heavily for center of mass stability
def sample_path(path_d, n=200):
    try:
        p = parse_path(path_d)
        pts = []
        for i in range(n):
            if p.length() == 0: pts.append((0,0)); continue
            c = p.point(i / float(n - 1))
            pts.append((c.real, c.imag))
        return pts
    except: return [(0,0)] * n

def bbox_center(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return min(xs)+(max(xs)-min(xs))/2.0, min(ys)+(max(ys)-min(ys))/2.0

def mean_centroid(pts):
    return sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts)

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

import ast

with open('태피티피_플레이.html', 'r', encoding='utf-8') as f:
    html = f.read()

m = re.search(r'const rawSvgPresets = (\[.*?\]);', html, re.DOTALL)
presets_raw = ast.literal_eval(m.group(1).replace('\n', ''))

base_shapes = presets_raw[0]
base_data = []
for i, html_str in enumerate(base_shapes):
    pts = sample_path(get_d(html_str))
    base_data.append({
        'idx': i,
        'html': html_str,
        'color': get_color(html_str),
        'len': shape_len(get_d(html_str)),
        'pts': pts,
        'bcx': bbox_center(pts)[0],
        'bcy': bbox_center(pts)[1]
    })

base_grouped = {}
for b in base_data:
    base_grouped.setdefault(b['color'], []).append(b)
for col in base_grouped:
    base_grouped[col].sort(key=lambda x: x['len'])

all_matrices = []

for p_idx, preset in enumerate(presets_raw):
    target_data = []
    for i, html_str in enumerate(preset):
        d = get_d(html_str)
        unscaled_pts = sample_path(d)
        upscaled_pts = [(x*SCALE, y*SCALE) for x,y in unscaled_pts]
        target_data.append({
            'idx': i,
            'html': html_str,
            'color': get_color(html_str),
            'len': shape_len(d), # sort unscaled len
            'pts': upscaled_pts,
        })
        
    target_grouped = {}
    for t in target_data:
        target_grouped.setdefault(t['color'], []).append(t)
    for col in target_grouped:
        target_grouped[col].sort(key=lambda x: x['len'])
        
    matrix_state = [{'x':0,'y':0,'r':0,'f':1} for _ in range(7)]
    
    for col, b_list in base_grouped.items():
        if col not in target_grouped: continue
        t_list = target_grouped[col]
        for idx_in_col, b in enumerate(b_list):
            if idx_in_col >= len(t_list): break
            t = t_list[idx_in_col]
            
            # Use basic transform (no translation) to find pure rotational offset error
            best_r, best_f, best_err = 0, 1, float('inf')
            
            # Since CSS transform translates the shape AFTER rotation, around 'bcx, bcy'
            for f in [1, -1]:
                for r in range(0, 360, 15):
                    # test pure rotation
                    test_pts = transform_pts(b['pts'], 0, 0, r, f, b['bcx'], b['bcy'])
                    
                    # Instead of exhaustive NN search for DX/DY, determine analytical dx/dy
                    t_mx, t_my = mean_centroid(t['pts'])
                    c_mx, c_my = mean_centroid(test_pts)
                    
                    dx = t_mx - c_mx
                    dy = t_my - c_my
                    
                    # shift test_pts to see if it's a good shape match
                    shifted_pts = [(p[0]+dx, p[1]+dy) for p in test_pts]
                    
                    # compute alignment error
                    err = sum(min(math.hypot(tp[0]-sp[0], tp[1]-sp[1]) for sp in shifted_pts) for tp in t['pts']) / len(t['pts'])
                    if err < best_err:
                        best_err = err
                        best_r = r
                        best_f = f
                        best_dx = dx
                        best_dy = dy
                        
            matrix_state[b['idx']] = {'x': round(best_dx,1), 'y': round(best_dy,1), 'r': best_r, 'f': best_f}
    
    # Base configuration pose_cx and shift
    all_xs = [p[0] for t in target_data for p in t['pts']]
    all_ys = [p[1] for t in target_data for p in t['pts']]
    pose_cx = min(all_xs) + (max(all_xs)-min(all_xs))/2
    pose_cy = min(all_ys) + (max(all_ys)-min(all_ys))/2
    
    base_xs = [p[0] for base in base_data for p in base['pts']]
    base_ys = [p[1] for base in base_data for p in base['pts']]
    targetX = min(base_xs) + (max(base_xs)-min(base_xs))/2
    targetY = min(base_ys) + (max(base_ys)-min(base_ys))/2
    
    shift_x = targetX - pose_cx
    shift_y = targetY - pose_cy
    
    for state in matrix_state:
        state['x'] = round(state['x'] + shift_x, 2)
        state['y'] = round(state['y'] + shift_y, 2)
        
    all_matrices.append(matrix_state)

with open('perfect_matrices_v2.json', 'w') as f:
    json.dump(all_matrices, f, indent=4)
print("Saved perfect_matrices_v2.json successfully!")
