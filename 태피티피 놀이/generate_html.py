import json

# read the original file to grab rawSvgPresets safely
with open('태피티피_플레이.html', 'r', encoding='utf-8') as f:
    orig = f.read()

import re
m = re.search(r'const rawSvgPresets = \[.*?\];', orig, re.DOTALL)
if m:
    rawSvgPresets_str = m.group(0)
else:
    print("Failed to find rawSvgPresets")
    exit(1)

html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>태피티피 제너레이티브 플레이그라운드</title>
  <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    body, html {{
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      background: linear-gradient(135deg, #f5f7fa 0%, #eef1f6 100%);
      font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, 'Helvetica Neue', sans-serif;
      overflow: hidden;
      user-select: none;
    }}

    .bg-grid {{
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      background-image: radial-gradient(#cbd4e1 1.5px, transparent 1.5px);
      background-size: 30px 30px;
      z-index: 0;
      opacity: 0.7;
      pointer-events: none;
    }}

    header {{
      position: absolute;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      padding: 16px 32px;
      background: rgba(255, 255, 255, 0.75);
      border-radius: 24px;
      box-shadow: 
        0 4px 24px -6px rgba(0,0,0,0.06),
        0 1px 4px rgba(0,0,0,0.04),
        inset 0 0 0 1px rgba(255,255,255,0.4);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      z-index: 100;
      display: flex;
      justify-content: space-between;
      align-items: center;
      min-width: 600px;
      max-width: 90vw;
    }}

    .header-text {{ display: flex; flex-direction: column; gap: 4px; }}
    h1 {{ margin: 0; font-size: 1.25rem; font-weight: 800; color: #1e1b4b; letter-spacing: -0.02em; }}
    .instructions {{ font-size: 0.9rem; color: #64748b; display: flex; align-items: center; gap: 6px; }}

    kbd {{
      background: #ffffff; border-radius: 6px; border: 1px solid #e2e8f0;
      box-shadow: 0 1px 2px rgba(0,0,0,0.05); color: #334155;
      display: inline-flex; align-items: center; justify-content: center;
      font-size: 0.8rem; font-weight: 600; padding: 2px 8px; height: 20px;
    }}

    #controls {{ display: flex; gap: 12px; }}

    button {{
      padding: 10px 20px; border: none; background: #302783; color: white;
      border-radius: 12px; font-family: 'Pretendard', sans-serif; font-weight: 700;
      font-size: 0.9rem; cursor: pointer;
      box-shadow: 0 4px 12px rgba(48, 39, 131, 0.25);
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    button:hover {{ background: #e94f35; box-shadow: 0 6px 16px rgba(233, 79, 53, 0.3); transform: translateY(-1px); }}
    button:active {{ transform: translateY(1px); box-shadow: 0 2px 8px rgba(233, 79, 53, 0.2); }}
    
    #preset-dock {{
      position: absolute;
      bottom: 30px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(255, 255, 255, 0.85);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      padding: 14px 24px;
      border-radius: 24px;
      box-shadow: 0 10px 30px -10px rgba(0,0,0,0.15), inset 0 0 0 1px rgba(255,255,255,0.7);
      display: flex;
      align-items: center;
      gap: 20px;
      z-index: 100;
      max-width: 90vw;
      overflow-x: auto;
    }}
    
    .dock-title {{
      font-weight: 800;
      color: #1e1b4b;
      font-size: 0.95rem;
      white-space: nowrap;
    }}
    
    #preset-list {{ display: flex; gap: 10px; }}
    
    .preset-btn {{
      width: 44px; height: 44px;
      border-radius: 12px;
      background: #f1f5f9;
      border: 2px solid transparent;
      cursor: pointer; display: flex; align-items: center; justify-content: center;
      font-weight: 800; color: #64748b; font-size: 1rem; transition: all 0.2s; flex-shrink: 0;
    }}
    .preset-btn:hover {{ border-color: #302783; color: #302783; transform: scale(1.05); }}
    .preset-btn.active {{ background: #302783; color: white; border-color: #302783; }}
    
    .btn-save {{ background: #10b981; padding: 10px 16px; white-space: nowrap; box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25); }}
    .btn-save:hover {{ background: #059669; box-shadow: 0 6px 16px rgba(16, 185, 129, 0.3); }}

    #canvas-container {{ width: 100%; height: 100%; position: relative; z-index: 1; }}
    svg {{ width: 100%; height: 100%; display: block; overflow: visible; }}
    
    .piece {{
      cursor: grab;
      filter: drop-shadow(0 4px 6px rgba(48, 39, 131, 0.15)) drop-shadow(0 1px 3px rgba(0,0,0,0.08));
      transition: filter 0.3s ease;
      transform-style: preserve-3d; 
    }}
    .piece.selected {{ filter: drop-shadow(0 15px 25px rgba(48, 39, 131, 0.25)) drop-shadow(0 5px 10px rgba(0,0,0,0.1)); }}
    .piece:active {{ cursor: grabbing; }}
    .piece.selected polygon, .piece.selected path {{
      stroke-width: 2.5; stroke: rgba(255, 255, 255, 0.9); stroke-linejoin: round;
    }}
  </style>
</head>
<body>
  <div class="bg-grid"></div>

  <header>
    <div class="header-text">
      <h1>태피티피 제너레이티브 플레이그라운드</h1>
      <div class="instructions">
        조각 선택 후 <kbd>R</kbd> 혹은 <kbd>←</kbd> <kbd>→</kbd> 로 회전 / <kbd>F</kbd> 로 좌우반전 (격자 스냅)
      </div>
    </div>
    <div id="controls">
      <button id="btn-scatter">랜덤 분해</button>
      <button id="btn-reset">로고 원본</button>
    </div>
  </header>
  
  <div id="canvas-container">
    <svg id="game-svg" xmlns="http://www.w3.org/2000/svg" viewBox="-250 -150 1342 1000" preserveAspectRatio="xMidYMid meet">
    </svg>
  </div>

  <div id="preset-dock">
    <div class="dock-title">포즈 프리셋 ✨</div>
    <div id="preset-list"></div>
    <button id="btn-save" class="btn-save">+ 현재 포즈 추가</button>
    <button id="btn-clear" class="btn-save" style="background:#e94f35; margin-left:10px;">초기화</button>
  </div>

<script>
{rawSvgPresets_str}

  const svgNS = "http://www.w3.org/2000/svg";
  const svgCanvas = document.getElementById('game-svg');
  
  const SCALE_FACTOR = 7.1718335;
  function upscaleSVGHTML(htmlStr) {{
      if(!htmlStr) return '';
      let s = htmlStr;
      s = s.replace(/points="([^"]+)"/, (match, pts) => {{
          const scaledPts = pts.trim().split(/[, \\n\\r]+/).filter(Boolean).map(Number).map(n => n * SCALE_FACTOR).join(" ");
          return `points="${{scaledPts}}"`;
      }});
      s = s.replace(/d="([^"]+)"/, (match, d) => {{
          return 'd="' + d.replace(/([-\d.]+)/g, m => Number(m) * SCALE_FACTOR) + '"';
      }});
      return s;
  }}

  // Prepare shapes properly upscaled and centered
  const hiddenSvg = document.createElementNS(svgNS, 'svg');
  hiddenSvg.style.position = 'absolute';
  hiddenSvg.style.visibility = 'hidden';
  document.body.appendChild(hiddenSvg);

  const processedPresets = rawSvgPresets.map((presetArr, idx) => {{
      if(idx === 0) return presetArr.map(html => ({{html, x:0, y:0, r:0, f:1}}));
      
      const group = document.createElementNS(svgNS, 'g');
      hiddenSvg.appendChild(group);
      
      const upscaledData = presetArr.map(html => upscaleSVGHTML(html));
      upscaledData.forEach(html => {{
          const p = document.createElementNS(svgNS, 'g');
          p.innerHTML = html;
          group.appendChild(p);
      }});
      
      const bbox = group.getBBox();
      const cx = bbox.x + bbox.width/2;
      const cy = bbox.y + bbox.height/2;
      
      const targetX = 421;
      const targetY = 266;
      const shiftX = targetX - cx;
      const shiftY = targetY - cy;
      group.remove();
      
      return upscaledData.map(html => ({{
          html: html,
          x: shiftX,
          y: shiftY,
          r: 0,
          f: 1
      }}));
  }});

  let customPresets = JSON.parse(localStorage.getItem('tepitipi_custom_presets_v5'));
  if (!customPresets || customPresets.length === 0) {{
    customPresets = processedPresets.slice(1);
    localStorage.setItem('tepitipi_custom_presets_v5', JSON.stringify(customPresets));
  }}

  let selectedPiece = null;
  const pieces = [];
  let isDragging = false;
  let startCoord = {{x: 0, y: 0}};

  // Base Logo Init
  rawSvgPresets[0].forEach((elementStr) => {{
    const group = document.createElementNS(svgNS, 'g');
    group.classList.add('piece');
    group.innerHTML = elementStr;
    group.state = {{ x: 0, y: 0, r: 0, cx: 0, cy: 0, f: 1 }};
    svgCanvas.appendChild(group);
    pieces.push(group);
  }});

  requestAnimationFrame(() => {{
    pieces.forEach(p => {{
      const bbox = p.getBBox();
      p.state.cx = bbox.x + bbox.width / 2;
      p.state.cy = bbox.y + bbox.height / 2;
      p.style.transformOrigin = `${{p.state.cx}}px ${{p.state.cy}}px`;
      updateTransform(p);
    }});
  }});

  function updateTransform(p) {{
    p.style.transform = `translate(${{p.state.x}}px, ${{p.state.y}}px) rotate(${{p.state.r}}deg) scaleX(${{p.state.f}})`;
  }}

  function getMousePos(evt) {{
    const CTM = svgCanvas.getScreenCTM();
    if(evt.touches) return {{ x: (evt.touches[0].clientX - CTM.e) / CTM.a, y: (evt.touches[0].clientY - CTM.f) / CTM.d }};
    return {{ x: (evt.clientX - CTM.e) / CTM.a, y: (evt.clientY - CTM.f) / CTM.d }};
  }}

  function getShapeAnchors(p) {{
    if (!p.anchorCache) {{
        const anchors = [];
        const shapeNode = p.firstElementChild;
        if (shapeNode && shapeNode.tagName.toLowerCase() === 'path' && shapeNode.getTotalLength) {{
            const len = shapeNode.getTotalLength();
            if (len > 0) {{
                for (let i = 0; i < 24; i++) {{
                    let pt = shapeNode.getPointAtLength(len * (i / 23));
                    anchors.push({{x: pt.x, y: pt.y}});
                }}
            }}
        }} else if (shapeNode && shapeNode.tagName.toLowerCase() === 'polygon' && shapeNode.points) {{
            const pts = shapeNode.points;
            if (pts.numberOfItems >= 3) {{
                for (let i = 0; i < pts.numberOfItems; i++) {{
                    let p1 = pts.getItem(i);
                    let p2 = pts.getItem((i+1) % pts.numberOfItems);
                    for (let j = 0; j < 6; j++) {{
                        anchors.push({{
                            x: p1.x + (p2.x - p1.x) * (j / 6),
                            y: p1.y + (p2.y - p1.y) * (j / 6)
                        }});
                    }}
                }}
            }}
        }}
        const box = p.getBBox();
        anchors.push({{x: box.x + box.width/2, y: box.y + box.height/2}});
        p.anchorCache = anchors;
    }}
    const cx = p.state.cx;
    const cy = p.state.cy;
    const rad = p.state.r * Math.PI / 180;
    const cosR = Math.cos(rad);
    const sinR = Math.sin(rad);
    return p.anchorCache.map(pt => {{
        let lx = cx + (pt.x - cx) * p.state.f;
        let ly = pt.y;
        let dx = lx - cx;
        let dy = ly - cy;
        let rx = cx + dx * cosR - dy * sinR;
        let ry = cy + dx * sinR + dy * cosR;
        return {{ x: rx + p.state.x, y: ry + p.state.y }};
    }});
  }}

  svgCanvas.addEventListener('mousedown', startDrag);
  svgCanvas.addEventListener('mousemove', drag);
  window.addEventListener('mouseup', endDrag);
  svgCanvas.addEventListener('touchstart', startDrag, {{passive: false}});
  svgCanvas.addEventListener('touchmove', drag, {{passive: false}});
  window.addEventListener('touchend', endDrag);

  function selectPiece(p) {{
    if (selectedPiece === p) return;
    if (selectedPiece) selectedPiece.classList.remove('selected');
    selectedPiece = p;
    if (p) {{ p.classList.add('selected'); svgCanvas.appendChild(p); }}
  }}

  function startDrag(evt) {{
    const targetGroup = evt.target.closest('g.piece');
    if (!targetGroup) return selectPiece(null);
    evt.preventDefault();
    selectPiece(targetGroup);
    isDragging = true;
    const coord = getMousePos(evt);
    startCoord.x = coord.x - targetGroup.state.x;
    startCoord.y = coord.y - targetGroup.state.y;
    targetGroup.style.transition = 'none';
  }}

  function drag(evt) {{
    if (!isDragging || !selectedPiece) return;
    evt.preventDefault();
    const coord = getMousePos(evt);
    let nx = coord.x - startCoord.x;
    let ny = coord.y - startCoord.y;
    
    if(nx < -500) nx = -500;
    if(nx > 1000) nx = 1000;
    if(ny < -500) ny = -500;
    if(ny > 800) ny = 800;

    selectedPiece.state.x = nx;
    selectedPiece.state.y = ny;
    updateTransform(selectedPiece);
  }}

  function endDrag(evt) {{
    if (!isDragging || !selectedPiece) return;
    isDragging = false;
    selectedPiece.style.transition = 'transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275)'; 
    let bestSnap = null;
    let bestDist = 20; 
    const myAnchors = getShapeAnchors(selectedPiece);
    pieces.forEach(target => {{
        if(target === selectedPiece) return;
        const targetAnchors = getShapeAnchors(target);
        myAnchors.forEach(mPt => {{
            targetAnchors.forEach(tPt => {{
                const d = Math.hypot(mPt.x - tPt.x, mPt.y - tPt.y);
                if (d < bestDist) {{
                    bestDist = d;
                    bestSnap = {{ dx: tPt.x - mPt.x, dy: tPt.y - mPt.y }};
                }}
            }});
        }});
    }});
    if (bestSnap) {{
        selectedPiece.state.x += bestSnap.dx;
        selectedPiece.state.y += bestSnap.dy;
    }}
    updateTransform(selectedPiece);
    setTimeout(() => {{ if(selectedPiece) selectedPiece.style.transition = 'filter 0.3s ease'; }}, 200);
  }}

  window.addEventListener('keydown', (e) => {{
    if (!selectedPiece) return;
    if (e.key === 'f' || e.key === 'F') {{
      e.preventDefault();
      selectedPiece.state.f *= -1; 
      selectedPiece.style.transition = 'transform 0.2s cubic-bezier(0.4, 0, 0.2, 1)';
      updateTransform(selectedPiece);
      setTimeout(() => {{ if(selectedPiece) selectedPiece.style.transition = 'filter 0.3s ease'; }}, 200);
      return;
    }}
    let angleChange = 0;
    if (e.key === 'r' || e.key === 'R' || e.key === 'ArrowRight') angleChange = 15;
    else if (e.key === 'ArrowLeft') angleChange = -15;
    if (angleChange !== 0) {{
      e.preventDefault();
      selectedPiece.state.r = (selectedPiece.state.r + angleChange) % 360; 
      selectedPiece.style.transition = 'transform 0.2s cubic-bezier(0.4, 0, 0.2, 1)';
      updateTransform(selectedPiece);
      setTimeout(() => {{ if(selectedPiece) selectedPiece.style.transition = 'filter 0.3s ease'; }}, 200);
    }}
  }});

  document.getElementById('btn-reset').addEventListener('click', () => {{
    applyPresetData(processedPresets[0]);
    updatePresetUI(-1);
  }});

  document.getElementById('btn-scatter').addEventListener('click', () => {{
    const randomPreset = pieces.map(p => ({{
        html: p.innerHTML,
        x: (Math.random() - 0.5) * 600,
        y: (Math.random() - 0.5) * 600,
        r: Math.floor(Math.random() * 24) * 15,
        f: Math.random() > 0.5 ? 1 : -1
    }}));
    applyPresetData(randomPreset);
    updatePresetUI(-1);
  }});

  const presetListEl = document.getElementById('preset-list');
  function renderPresetButtons() {{
      presetListEl.innerHTML = '';
      customPresets.forEach((_, idx) => {{
          const btn = document.createElement('div');
          btn.className = 'preset-btn';
          btn.innerText = idx + 1;
          btn.onclick = () => {{
              applyPresetData(customPresets[idx]);
              updatePresetUI(idx);
          }};
          presetListEl.appendChild(btn);
      }});
  }}

  function applyPresetData(presetArr) {{
      pieces.forEach((p, i) => {{
        if (!presetArr[i]) return;
        
        const oldBBox = p.getBBox();
        const oldVisX = (oldBBox.x + oldBBox.width/2) + p.state.x;
        const oldVisY = (oldBBox.y + oldBBox.height/2) + p.state.y;
        
        p.style.transition = 'none'; 
        p.innerHTML = presetArr[i].html;
        p.anchorCache = null; 
        
        const newTargetX = presetArr[i].x || 0;
        const newTargetY = presetArr[i].y || 0;
        const newTargetR = presetArr[i].r || 0;
        const newTargetF = presetArr[i].f || 1;
        
        const newBBox = p.getBBox();
        const new_cx = newBBox.x + newBBox.width / 2;
        const new_cy = newBBox.y + newBBox.height / 2;
        
        const teleportX = oldVisX - new_cx;
        const teleportY = oldVisY - new_cy;
        const oldR = p.state.r;
        const oldF = p.state.f;
        
        p.style.transformOrigin = `${{new_cx}}px ${{new_cy}}px`;
        p.style.transform = `translate(${{teleportX}}px, ${{teleportY}}px) rotate(${{oldR}}deg) scaleX(${{oldF}})`;
        
        void p.offsetWidth;
        
        p.style.transition = 'transform 0.8s cubic-bezier(0.25, 1, 0.5, 1)';
        
        p.state.x = newTargetX;
        p.state.y = newTargetY;
        p.state.r = newTargetR;
        p.state.f = newTargetF;
        p.state.cx = new_cx;
        p.state.cy = new_cy;
        
        updateTransform(p);
      }});
      setTimeout(() => {{ pieces.forEach(p => p.style.transition = 'filter 0.3s ease'); }}, 800);
  }}

  function updatePresetUI(activeIndex) {{
      const btns = presetListEl.querySelectorAll('.preset-btn');
      btns.forEach((b, i) => {{
          if (i === activeIndex) b.classList.add('active');
          else b.classList.remove('active');
      }});
  }}

  document.getElementById('btn-save').addEventListener('click', () => {{
      const currentState = pieces.map(p => ({{
          html: p.innerHTML,
          x: p.state.x,
          y: p.state.y,
          r: p.state.r,
          f: p.state.f
      }}));
      customPresets.push(currentState);
      localStorage.setItem('tepitipi_custom_presets_v5', JSON.stringify(customPresets));
      renderPresetButtons();
      updatePresetUI(customPresets.length - 1);
  }});

  document.getElementById('btn-clear').addEventListener('click', () => {{
      if(confirm('진짜로 초기화할까요?')) {{
          localStorage.removeItem('tepitipi_custom_presets_v5');
          location.reload();
      }}
  }});

  renderPresetButtons();
</script>
</body>
</html>
"""

with open('태피티피_플레이.html', 'w', encoding='utf-8') as f:
    f.write(html_content)
