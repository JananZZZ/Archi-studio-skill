from __future__ import annotations

from pathlib import Path
import json
from .presets import PRESETS


def build_editor(project_svg: str, technical_svg: str, config: dict, specs: dict, out: str | Path) -> Path:
    data = json.dumps({"config": config, "specs": specs, "palettes": PRESETS}, ensure_ascii=False)
    html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Archi Studio Interactive Editor</title>
<style>
:root{{--panel:#fff;--bg:#f5f7fb;--line:#d9e0ea;--ink:#101828;--muted:#667085;--blue:#2f6bff}}
*{{box-sizing:border-box}} body{{margin:0;font-family:Inter,"Noto Sans CJK SC","Microsoft YaHei",sans-serif;background:var(--bg);color:var(--ink)}}
.app{{display:grid;grid-template-columns:320px 1fr;height:100vh}} aside{{background:#fff;border-right:1px solid var(--line);padding:20px;overflow:auto}} main{{padding:18px;overflow:auto}}
h1{{font-size:20px;margin:0 0 6px}} .sub{{font-size:12px;color:var(--muted);margin-bottom:18px}} label{{display:block;font-size:13px;font-weight:650;margin:14px 0 6px}}
select,input[type=range],input[type=text]{{width:100%}} select,input[type=text]{{height:36px;border:1px solid var(--line);border-radius:9px;padding:0 10px;background:#fff}}
button{{border:0;background:var(--blue);color:#fff;border-radius:9px;padding:9px 12px;font-weight:650;cursor:pointer;margin-right:6px;margin-top:10px}} button.secondary{{background:#eef4ff;color:#234fb9}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px;align-items:start}} .card{{background:#fff;border:1px solid var(--line);border-radius:16px;padding:12px;box-shadow:0 4px 18px rgba(16,24,40,.06)}}
.card h2{{font-size:14px;margin:0 0 10px}} .canvas{{width:100%;aspect-ratio:1/2;overflow:auto;background:#fff;border-radius:12px}} .canvas svg{{width:100%;height:auto;display:block}}
.small{{font-size:11px;color:var(--muted);line-height:1.5}} pre{{white-space:pre-wrap;font-size:11px;background:#f7f9fc;padding:10px;border-radius:10px;max-height:220px;overflow:auto}}
@media(max-width:980px){{.app{{grid-template-columns:1fr}} aside{{border-right:0;border-bottom:1px solid var(--line)}} .grid{{grid-template-columns:1fr}}}}
</style></head>
<body><div class="app"><aside><h1>Archi Studio</h1><div class="sub">交互式调节器 · 不修改原始证据，只调整视觉与可见内容</div>
<label>配色方案</label><select id="palette"><option>cool-professional</option><option>portfolio-premium</option><option>academic-light</option><option>warm-business</option></select>
<label>字体缩放 <span id="typeVal"></span></label><input id="typeScale" type="range" min="0.85" max="1.18" step="0.01">
<label>间距缩放 <span id="spaceVal"></span></label><input id="spaceScale" type="range" min="0.85" max="1.20" step="0.01">
<label>内容密度</label><select id="density"><option value="concise">concise</option><option value="balanced">balanced</option><option value="detailed">detailed</option></select>
<label>修改标题（即时预览）</label><input id="titleText" type="text" placeholder="输入新标题">
<button onclick="applyLocal()">应用预览</button><button class="secondary" onclick="downloadConfig()">导出配置</button>
<button class="secondary" onclick="downloadSVG('project')">导出项目 SVG</button><button class="secondary" onclick="downloadSVG('technical')">导出技术 SVG</button><button class="secondary" onclick="downloadPNG('project')">导出项目 PNG</button><button class="secondary" onclick="downloadPNG('technical')">导出技术 PNG</button>
<p class="small">提示：浏览器编辑器用于轻量交互。结构性修改（合并模块、重排层级、精简 20%）建议在 Agent 中通过自然语言修改 spec/config 后重新运行完整 QA。</p>
<label>当前配置</label><pre id="configView"></pre></aside>
<main><div class="grid"><div class="card"><h2>Project Architecture</h2><div class="canvas" id="project">{project_svg}</div></div><div class="card"><h2>Technical Architecture</h2><div class="canvas" id="technical">{technical_svg}</div></div></div></main></div>
<script>
const bundle={data}; const cfg=bundle.config;
const palette=document.getElementById('palette'), typeScale=document.getElementById('typeScale'), spaceScale=document.getElementById('spaceScale'), density=document.getElementById('density');
palette.value=cfg.palette||'portfolio-premium'; typeScale.value=cfg.typography_scale||1; spaceScale.value=cfg.spacing_scale||1; density.value=cfg.density||'balanced';
function sync(){{cfg.palette=palette.value;cfg.typography_scale=Number(typeScale.value);cfg.spacing_scale=Number(spaceScale.value);cfg.density=density.value;document.getElementById('typeVal').textContent=cfg.typography_scale.toFixed(2);document.getElementById('spaceVal').textContent=cfg.spacing_scale.toFixed(2);document.getElementById('configView').textContent=JSON.stringify(cfg,null,2)}}
[palette,typeScale,spaceScale,density].forEach(el=>el.addEventListener('input',sync)); sync();
const originalPalette=cfg.palette||'portfolio-premium';
function flattenPalette(name){{const p=bundle.palettes[name], m={{}}; if(!p)return m; ['background','ink','muted','line'].forEach(k=>{{if(p[k])m[k]=p[k]}}); ['blue','cyan','purple','orange','green','red','slate'].forEach(k=>{{if(p[k]){{m[k+'-stroke']=p[k][0];m[k+'-fill']=p[k][1]}}}}); return m}}
const basePal=flattenPalette(originalPalette);
document.querySelectorAll('.canvas svg').forEach(svg=>{{svg.querySelectorAll('text').forEach(t=>t.dataset.baseSize=t.getAttribute('font-size')||'12')}});
function recolor(svg,targetName){{const target=flattenPalette(targetName); const pairs=[]; Object.keys(basePal).forEach(k=>{{if(target[k])pairs.push([basePal[k].toLowerCase(),target[k]])}}); svg.querySelectorAll('*').forEach(el=>{{['fill','stroke'].forEach(attr=>{{const val=(el.getAttribute(attr)||'').toLowerCase(); for(const [from,to] of pairs){{if(val===from){{el.setAttribute(attr,to);break}}}}}})}})}}
function applyLocal(){{sync(); const title=document.getElementById('titleText').value.trim(); document.querySelectorAll('.canvas svg').forEach((svg,idx)=>{{recolor(svg,cfg.palette); svg.querySelectorAll('text').forEach(t=>{{const base=Number(t.dataset.baseSize||t.getAttribute('font-size')||12); t.setAttribute('font-size',(base*cfg.typography_scale).toFixed(2))}}); if(title){{const texts=svg.querySelectorAll('text'); if(texts[1]) texts[1].textContent=title+(idx===0?'｜项目架构图':'｜技术架构图')}}}})}}
function saveBlob(name,text,type){{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{{type}}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),500)}}
function downloadConfig(){{sync();saveBlob('diagram.config.json',JSON.stringify(cfg,null,2),'application/json')}}
function getSVG(kind){{return document.querySelector('#'+kind+' svg')}}
function downloadSVG(kind){{const svg=getSVG(kind).outerHTML;saveBlob(kind+'_architecture.svg',svg,'image/svg+xml')}}
function downloadPNG(kind){{const svg=getSVG(kind);const xml=new XMLSerializer().serializeToString(svg);const blob=new Blob([xml],{{type:'image/svg+xml;charset=utf-8'}});const url=URL.createObjectURL(blob);const img=new Image();img.onload=()=>{{const vb=svg.viewBox.baseVal;const scale=2;const canvas=document.createElement('canvas');canvas.width=Math.round(vb.width*scale);canvas.height=Math.round(vb.height*scale);const ctx=canvas.getContext('2d');ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(img,0,0,canvas.width,canvas.height);URL.revokeObjectURL(url);canvas.toBlob(png=>{{const a=document.createElement('a');a.href=URL.createObjectURL(png);a.download=kind+'_architecture.png';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),800)}},'image/png')}};img.onerror=()=>{{URL.revokeObjectURL(url);alert('PNG export failed')}};img.src=url}}
</script></body></html>'''
    p = Path(out)
    p.write_text(html, encoding="utf-8")
    return p
