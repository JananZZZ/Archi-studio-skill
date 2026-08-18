import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from archi_studio.models import Preferences
from archi_studio.intake import analyze_project
from archi_studio.planner import plan_project
from archi_studio.layout import layout_diagram
from archi_studio.renderer import render_svg
from archi_studio.export import export_svg

ROOT=Path(__file__).resolve().parents[1]
SAMPLE=ROOT/'examples'/'sample_input'
OUT=ROOT/'presets'
model=analyze_project(SAMPLE)
for palette in ['cool-professional','portfolio-premium','academic-light','warm-business']:
    p=Preferences(palette=palette, mode='portfolio', density='concise')
    spec=plan_project(model,p)
    layout=layout_diagram(spec,p)
    svg=OUT/f'{palette}.svg'
    render_svg(spec,layout,p,svg)
    export_svg(svg,make_png=True,make_pdf=False)
    print(svg)