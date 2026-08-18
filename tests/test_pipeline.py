from pathlib import Path
from archi_studio.intake import analyze_project
from archi_studio.models import Preferences
from archi_studio.planner import plan_dual
from archi_studio.layout import layout_diagram
from archi_studio.quality import inspect
from archi_studio.renderer import render_svg

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "sample_input"


def test_intake_and_plan():
    model = analyze_project(SAMPLE)
    assert model.name
    assert "React" in sum(model.tech_stack.values(), [])
    p, t = plan_dual(model, Preferences())
    assert p.kind == "project"
    assert t.kind == "technical"
    assert len(p.sections) >= 4
    assert len(t.sections) >= 4


def test_layout_and_svg():
    model = analyze_project(SAMPLE)
    p, _ = plan_dual(model, Preferences())
    layout = layout_diagram(p, Preferences())
    critical = [x for x in inspect(layout, Preferences()) if x.severity == "critical"]
    assert not critical
    svg = render_svg(p, layout, Preferences())
    assert svg.startswith("<svg")
    assert "Project" in svg or "项目" in svg
