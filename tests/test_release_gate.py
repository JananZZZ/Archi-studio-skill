from pathlib import Path
import json, subprocess, sys, zipfile
import pytest
from archi_studio.intake import analyze_project, _contains_term
from archi_studio.models import Preferences
from archi_studio.orchestrator import ArchiStudio
from archi_studio.questionnaire import interactive_questionnaire
from archi_studio.questionnaire_web import build_questionnaire
from archi_studio.presets import PRESETS

ROOT=Path(__file__).resolve().parents[1]
SAMPLE=ROOT/'examples'/'sample_input'

def test_term_boundary():
    assert _contains_term('SSE event stream','sse')
    assert not _contains_term('assets directory','sse')

def test_sample_stack():
    m=analyze_project(SAMPLE)
    flat=sum(m.tech_stack.values(),[])
    assert 'React' in flat and 'Tauri' in flat and 'Rust' in flat

def test_examples_do_not_pollute_primary(tmp_path):
    (tmp_path/'README.md').write_text('# RealProject\n\nPython architecture tool',encoding='utf-8')
    ex=tmp_path/'examples'; ex.mkdir(); (ex/'README.md').write_text('# FakeReactDemo\nReact Tauri Rust',encoding='utf-8')
    m=analyze_project(tmp_path)
    assert m.name=='RealProject'
    assert 'React' not in sum(m.tech_stack.values(),[])

def test_questionnaire_defaults():
    answers=iter(['','','','','','',''])
    p=interactive_questionnaire(input_fn=lambda _ : next(answers), print_fn=lambda *_:None)
    assert p.mode=='portfolio' and p.interactive_editor

def test_all_presets_present():
    assert set(PRESETS)=={'cool-professional','portfolio-premium','academic-light','warm-business'}

def test_browser_questionnaire_build(tmp_path):
    p=build_questionnaire(tmp_path/'q.html')
    s=p.read_text(encoding='utf-8')
    assert 'diagram.config.json' in s and 'portfolio-premium' in s

@pytest.mark.parametrize('palette', list(PRESETS))
def test_build_all_palettes(tmp_path,palette):
    out=tmp_path/palette
    r=ArchiStudio().build(SAMPLE,out,Preferences(palette=palette),raster=False)
    assert not any(x['severity']=='critical' for xs in r['qa'].values() for x in xs)
    assert (out/'01_Project_Architecture.svg').exists()
    assert (out/'02_Technical_Architecture.svg').exists()
    assert (out/'interactive_editor.html').exists()
    assert (out/'questionnaire.html').exists()

def test_bundle_rerender(tmp_path):
    out=tmp_path/'bundle'; s=ArchiStudio(); s.build(SAMPLE,out,Preferences(),raster=False)
    specs=json.loads((out/'diagram_specs.json').read_text(encoding='utf-8'))
    specs['project']['title']='Changed Title'
    (out/'diagram_specs.json').write_text(json.dumps(specs,ensure_ascii=False),encoding='utf-8')
    s.render_from_bundle(out,raster=False)
    assert 'Changed Title' in (out/'01_Project_Architecture.svg').read_text(encoding='utf-8')

def test_package(tmp_path):
    out=tmp_path/'bundle'; s=ArchiStudio(); s.build(SAMPLE,out,Preferences(),raster=False)
    z=s.package(out,tmp_path/'bundle.zip')
    with zipfile.ZipFile(z) as f:
        names=set(f.namelist())
    assert '01_Project_Architecture.svg' in names and 'diagram.config.json' in names

def test_cli_help():
    p=subprocess.run([sys.executable,'-m','archi_studio.cli','--help'],cwd=ROOT,capture_output=True,text=True)
    assert p.returncode==0 and 'render-bundle' in p.stdout

def test_cli_config(tmp_path):
    cfg=tmp_path/'c.json'; cfg.write_text(json.dumps(Preferences().to_dict()),encoding='utf-8')
    out=tmp_path/'o'
    p=subprocess.run([sys.executable,'-m','archi_studio.cli','build',str(SAMPLE),'--out',str(out),'--config',str(cfg),'--no-raster'],cwd=ROOT,capture_output=True,text=True)
    assert p.returncode==0 and (out/'questionnaire.html').exists()

def test_raster_export(tmp_path):
    out=tmp_path/'raster'; ArchiStudio().build(SAMPLE,out,Preferences(),raster=True)
    for name in ['01_Project_Architecture.png','01_Project_Architecture.pdf','02_Technical_Architecture.png','02_Technical_Architecture.pdf','03_A4_SideBySide.pdf']:
        p=out/name; assert p.exists() and p.stat().st_size>1000
