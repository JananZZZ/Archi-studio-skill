from __future__ import annotations

from html import escape
from pathlib import Path
from .layout import LayoutResult
from .models import DiagramSpec, Preferences
from .presets import PRESETS
from .utils import wrap_text

FONT = "Noto Sans CJK SC, Microsoft YaHei, PingFang SC, Arial, sans-serif"


def _palette(name: str):
    return PRESETS.get(name, PRESETS["cool-professional"])


def _text(lines, x, y, size, weight=400, fill="#101828", anchor="middle", line_height=None):
    if isinstance(lines, str):
        lines = [lines]
    line_height = line_height or size * 1.18
    total = size + max(0, len(lines)-1) * line_height
    start = y - total/2 + size*0.78
    chunks = [f'<text x="{x:.2f}" y="{start:.2f}" font-family="{FONT}" font-size="{size:.2f}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">']
    for i, line in enumerate(lines):
        chunks.append(f'<tspan x="{x:.2f}" dy="{0 if i==0 else line_height:.2f}">{escape(str(line))}</tspan>')
    chunks.append('</text>')
    return ''.join(chunks)


def _wrapped(text: str, box_w: float, font_size: float, max_lines: int) -> list[str]:
    visual = max(12, int(box_w / max(6.0, font_size*0.56)))
    lines = wrap_text(text, visual)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        if lines:
            lines[-1] = lines[-1].rstrip("…") + "…"
    return lines


def render_svg(spec: DiagramSpec, layout: LayoutResult, prefs: Preferences, out: str | Path | None = None) -> str:
    pal = _palette(prefs.palette)
    W, H = layout.width, layout.height
    ink, muted, line = pal["ink"], pal["muted"], pal["line"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{prefs.width_mm}mm" height="{prefs.height_mm}mm" viewBox="0 0 {W} {H}">',
        '<defs>',
        '<filter id="shadow" x="-20%" y="-20%" width="140%" height="140%"><feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#AAB5C4" flood-opacity="0.14"/></filter>',
        f'<marker id="arrow" markerWidth="9" markerHeight="9" refX="7.5" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="{pal["blue"][0]}"/></marker>',
        '</defs>',
        f'<rect width="{W}" height="{H}" fill="{pal["background"]}"/>',
        f'<rect x="18" y="18" width="{W-36}" height="{H-36}" rx="30" fill="{pal["background"]}" stroke="{line}" stroke-width="2"/>',
        _text("ARCHI STUDIO · " + ("PROJECT ARCHITECTURE" if spec.kind == "project" else "TECHNICAL ARCHITECTURE"), 54, 58, 19*prefs.typography_scale, 760, pal["blue"][0], "start"),
        _text(spec.title, 54, 105, 42*prefs.typography_scale, 780, ink, "start"),
        _text(spec.subtitle, 54, 146, 19*prefs.typography_scale, 430, muted, "start"),
        f'<line x1="54" y1="169" x2="846" y2="169" stroke="{line}" stroke-width="2"/>',
    ]

    # Arrows between major section centers.
    sec_order = list(layout.section_bounds.items())
    for (_, a), (_, b) in zip(sec_order, sec_order[1:]):
        ax, ay, aw, ah = a; bx, by, bw, bh = b
        y1 = ay + ah + 1
        y2 = by - 4
        if y2 > y1:
            parts.append(f'<path d="M450 {y1:.2f} L450 {y2:.2f}" stroke="{pal["blue"][0]}" stroke-width="3" fill="none" marker-end="url(#arrow)"/>')

    # Draw headers then content.
    for box in layout.boxes:
        if box.kind != "section_header":
            continue
        p = box.payload
        stroke, fill = pal[p["color"]]
        parts.append(f'<rect x="{box.x:.2f}" y="{box.y:.2f}" width="{box.w:.2f}" height="{box.h:.2f}" rx="14" fill="{fill}" stroke="{fill}"/>')
        cx = box.x + 25; cy = box.y + box.h/2
        parts.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="16" fill="{stroke}"/>')
        parts.append(_text(str(p["index"]), cx, cy+1, 23*prefs.typography_scale, 780, "#FFFFFF"))
        parts.append(_text(p["title"], box.x+52, cy+1, 25*prefs.typography_scale, 760, ink, "start"))
        parts.append(_text(p["title_en"], box.x+box.w-18, cy+1, 18*prefs.typography_scale, 620, stroke, "end"))

    # Connect sibling node rows sequentially for evolution/flows.
    for sec_id, bound in layout.section_bounds.items():
        sx, sy, sw, sh = bound
        nodes = [b for b in layout.boxes if b.kind == "node" and sy < b.y < sy+sh]
        rows = {}
        for n in nodes:
            key = round(n.y / 10) * 10
            rows.setdefault(key, []).append(n)
        for row in rows.values():
            row.sort(key=lambda b: b.x)
            for a, b in zip(row, row[1:]):
                y = min(a.y+a.h/2, b.y+b.h/2)
                if b.x - (a.x+a.w) > 6:
                    parts.append(f'<path d="M{a.x+a.w:.2f} {y:.2f} L{b.x-5:.2f} {y:.2f}" stroke="{pal["blue"][0]}" stroke-width="2.4" fill="none" marker-end="url(#arrow)"/>')

    for box in layout.boxes:
        if box.kind not in {"node", "child_node", "note"}:
            continue
        if box.kind == "note":
            color = box.payload.get("color", "slate")
            stroke, fill = pal.get(color, pal["slate"])
            parts.append(f'<rect x="{box.x:.2f}" y="{box.y:.2f}" width="{box.w:.2f}" height="{box.h:.2f}" rx="11" fill="{fill}" stroke="{line}" stroke-width="1.5"/>')
            parts.append(_text(_wrapped(box.payload.get("text", ""), box.w-24, 15*prefs.typography_scale, 2), box.x+box.w/2, box.y+box.h/2, 15*prefs.typography_scale, 680, ink))
            continue
        p = box.payload
        color = p.get("color", "blue")
        stroke, fill = pal.get(color, pal["blue"])
        child = box.kind == "child_node"
        rx = 11 if child else 14
        shadow = '' if child else ' filter="url(#shadow)"'
        parts.append(f'<rect x="{box.x:.2f}" y="{box.y:.2f}" width="{box.w:.2f}" height="{box.h:.2f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{1.5 if child else 2}"{shadow}/>')
        title_size = (14 if child else 18) * prefs.typography_scale
        body_size = (11.5 if child else 14) * prefs.typography_scale
        title = p.get("title", "")
        subtitle = p.get("subtitle", "")
        body = p.get("body", [])
        # parent with children reserves upper half for summary
        upper_h = box.h*0.5 if p.get("children") else box.h
        lines = _wrapped(title, box.w-22, title_size, 2)
        title_y = box.y + upper_h*0.34
        parts.append(_text(lines, box.x+box.w/2, title_y, title_size, 740, ink))
        extra = []
        if subtitle:
            extra += _wrapped(subtitle, box.w-24, body_size, 1)
        for item in body[:3 if not child else 2]:
            extra += _wrapped(item, box.w-24, body_size, 1)
        if extra:
            extra_y = box.y + upper_h*0.70
            parts.append(_text(extra[:3], box.x+box.w/2, extra_y, body_size, 430, muted, line_height=body_size*1.16))

    parts.append(_text("Generated by Archi-studio-skill · SVG source of truth", 450, 1757, 12.5, 420, muted))
    parts.append('</svg>')
    svg = ''.join(parts)
    if out:
        Path(out).write_text(svg, encoding="utf-8")
    return svg
