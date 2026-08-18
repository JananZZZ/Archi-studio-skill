from __future__ import annotations

from pathlib import Path
import json
import shutil
import zipfile
from .models import Preferences, diagram_from_dict
from .intake import analyze_project
from .questionnaire import interactive_questionnaire
from .planner import plan_dual
from .layout import layout_diagram
from .quality import inspect, auto_adjust
from .renderer import render_svg
from .export import export_svg, compose_a4
from .editor import build_editor
from .questionnaire_web import build_questionnaire
from .utils import save_json


class ArchiStudio:
    def __init__(self, max_optimize_rounds: int = 3):
        self.max_optimize_rounds = max_optimize_rounds

    def build(self, source: str | Path, out_dir: str | Path, prefs: Preferences | None = None,
              interactive: bool = False, raster: bool = True) -> dict:
        source = Path(source)
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        model = analyze_project(source)
        prefs = prefs or (interactive_questionnaire() if interactive else Preferences())
        project_spec, technical_spec = plan_dual(model, prefs)

        reports = {}
        svgs = {}
        layouts = {}
        for spec in [project_spec, technical_spec]:
            local_prefs = Preferences(**prefs.to_dict())
            issues = []
            for _ in range(self.max_optimize_rounds):
                layout = layout_diagram(spec, local_prefs)
                issues = inspect(layout, local_prefs)
                if not any(i.severity == "critical" for i in issues) and len([i for i in issues if i.code == "TEXT_DENSITY"]) <= 2:
                    break
                local_prefs = auto_adjust(local_prefs, issues)
            layouts[spec.kind] = layout
            reports[spec.kind] = [i.to_dict() for i in issues]
            name = "01_Project_Architecture.svg" if spec.kind == "project" else "02_Technical_Architecture.svg"
            svg_path = out / name
            svg = render_svg(spec, layout, local_prefs, svg_path)
            svgs[spec.kind] = svg
            if raster:
                export_svg(svg_path, True, True)

        model.save(out / "project_model.json")
        save_json(out / "diagram_specs.json", {"project": project_spec.to_dict(), "technical": technical_spec.to_dict()})
        save_json(out / "diagram.config.json", prefs.to_dict())
        save_json(out / "qa_report.json", reports)
        save_json(out / "source_manifest.json", {
            "source": str(source.resolve()),
            "project_evidence_count": len(model.evidence),
            "generator": "Archi-studio-skill 1.0.0",
            "svg_source_of_truth": True,
        })
        build_questionnaire(out / "questionnaire.html", image_prefix="../presets")
        if prefs.interactive_editor:
            build_editor(svgs["project"], svgs["technical"], prefs.to_dict(),
                         {"project": project_spec.to_dict(), "technical": technical_spec.to_dict()},
                         out / "interactive_editor.html")
        ppdf, tpdf = out/"01_Project_Architecture.pdf", out/"02_Technical_Architecture.pdf"
        if raster and ppdf.exists() and tpdf.exists():
            compose_a4(ppdf, tpdf, out/"03_A4_SideBySide.pdf")

        return {
            "out_dir": str(out),
            "model": model.to_dict(),
            "preferences": prefs.to_dict(),
            "qa": reports,
        }

    def render_from_bundle(self, bundle_dir: str | Path, raster: bool = True) -> dict:
        """Re-render after an agent/user edits diagram_specs.json or diagram.config.json."""
        bundle = Path(bundle_dir)
        specs_data = json.loads((bundle / "diagram_specs.json").read_text(encoding="utf-8"))
        cfg = json.loads((bundle / "diagram.config.json").read_text(encoding="utf-8"))
        prefs = Preferences(**cfg)
        specs = [diagram_from_dict(specs_data["project"]), diagram_from_dict(specs_data["technical"])]
        reports, svgs = {}, {}
        for spec in specs:
            local_prefs = Preferences(**prefs.to_dict())
            issues = []
            for _ in range(self.max_optimize_rounds):
                layout = layout_diagram(spec, local_prefs)
                issues = inspect(layout, local_prefs)
                if not any(i.severity == "critical" for i in issues) and len([i for i in issues if i.code == "TEXT_DENSITY"]) <= 2:
                    break
                local_prefs = auto_adjust(local_prefs, issues)
            reports[spec.kind] = [i.to_dict() for i in issues]
            name = "01_Project_Architecture.svg" if spec.kind == "project" else "02_Technical_Architecture.svg"
            svg_path = bundle / name
            svgs[spec.kind] = render_svg(spec, layout, local_prefs, svg_path)
            if raster:
                export_svg(svg_path, True, True)
        save_json(bundle / "qa_report.json", reports)
        if prefs.interactive_editor:
            build_editor(svgs["project"], svgs["technical"], prefs.to_dict(), specs_data, bundle / "interactive_editor.html")
        ppdf, tpdf = bundle/"01_Project_Architecture.pdf", bundle/"02_Technical_Architecture.pdf"
        if raster and ppdf.exists() and tpdf.exists():
            compose_a4(ppdf, tpdf, bundle/"03_A4_SideBySide.pdf")
        return {"out_dir": str(bundle), "qa": reports}

    def package(self, out_dir: str | Path, zip_path: str | Path) -> Path:
        out_dir, zip_path = Path(out_dir), Path(zip_path)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            for p in out_dir.rglob("*"):
                if p.is_file() and p != zip_path:
                    z.write(p, p.relative_to(out_dir))
        return zip_path
