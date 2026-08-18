from __future__ import annotations

import argparse
from pathlib import Path
import http.server
import socketserver
import webbrowser
import json
from .models import Preferences
from .orchestrator import ArchiStudio
from .questionnaire import interactive_questionnaire


def cmd_build(args):
    if args.config:
        prefs = Preferences(**json.loads(Path(args.config).read_text(encoding='utf-8')))
    else:
        prefs = interactive_questionnaire() if not args.non_interactive else Preferences(
            mode=args.mode, density=args.density, palette=args.palette, language=args.language,
            emphasis=args.emphasis, interactive_editor=not args.no_editor,
        )
    studio = ArchiStudio()
    result = studio.build(args.source, args.out, prefs=prefs, interactive=False, raster=not args.no_raster)
    print(f"Built: {result['out_dir']}")
    print("QA:")
    for kind, issues in result["qa"].items():
        critical = sum(1 for x in issues if x["severity"] == "critical")
        warnings = sum(1 for x in issues if x["severity"] == "warning")
        print(f"  {kind}: {critical} critical, {warnings} warnings")


def cmd_init_demo(args):
    src = Path(__file__).resolve().parents[1] / "examples" / "sample_input"
    out = Path(__file__).resolve().parents[1] / "examples" / "sample_output"
    studio = ArchiStudio()
    studio.build(src, out, Preferences(), raster=not args.no_raster)
    print(out)


def cmd_serve(args):
    p = Path(args.html).resolve()
    root = p.parent
    handler = http.server.SimpleHTTPRequestHandler
    class Reuse(socketserver.TCPServer):
        allow_reuse_address = True
    import os
    os.chdir(root)
    with Reuse(("127.0.0.1", args.port), handler) as httpd:
        url = f"http://127.0.0.1:{args.port}/{p.name}"
        print(url)
        if not args.no_open:
            webbrowser.open(url)
        httpd.serve_forever()



def cmd_render_bundle(args):
    studio = ArchiStudio()
    result = studio.render_from_bundle(args.bundle, raster=not args.no_raster)
    print(f"Re-rendered: {result['out_dir']}")
    for kind, issues in result["qa"].items():
        critical = sum(1 for x in issues if x["severity"] == "critical")
        warnings = sum(1 for x in issues if x["severity"] == "warning")
        print(f"  {kind}: {critical} critical, {warnings} warnings")


def main():
    ap = argparse.ArgumentParser(prog="archi-studio", description="Automated dual architecture diagram studio")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="Analyze project and build architecture package")
    b.add_argument("source")
    b.add_argument("--out", default="architecture-output")
    b.add_argument("--non-interactive", action="store_true")
    b.add_argument("--config", help="Load diagram.config.json produced by questionnaire/editor")
    b.add_argument("--mode", default="portfolio", choices=["resume","portfolio","academic","business"])
    b.add_argument("--density", default="balanced", choices=["concise","balanced","detailed"])
    b.add_argument("--palette", default="portfolio-premium", choices=["cool-professional","portfolio-premium","academic-light","warm-business"])
    b.add_argument("--language", default="zh+en", choices=["zh+en","bilingual","zh","en"])
    b.add_argument("--emphasis", default="balanced", choices=["product_evolution","technical","balanced"])
    b.add_argument("--no-editor", action="store_true")
    b.add_argument("--no-raster", action="store_true", help="Skip PNG/PDF export")
    b.set_defaults(func=cmd_build)
    r = sub.add_parser("render-bundle", help="Re-render an existing editable bundle after JSON/config changes")
    r.add_argument("bundle")
    r.add_argument("--no-raster", action="store_true")
    r.set_defaults(func=cmd_render_bundle)
    d = sub.add_parser("init-demo", help="Build bundled demo")
    d.add_argument("--no-raster", action="store_true")
    d.set_defaults(func=cmd_init_demo)
    s = sub.add_parser("serve-editor", help="Open local interactive editor")
    s.add_argument("html")
    s.add_argument("--port", type=int, default=8765)
    s.add_argument("--no-open", action="store_true")
    s.set_defaults(func=cmd_serve)
    args = ap.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
