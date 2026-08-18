from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any
from .models import DiagramSpec, Preferences


@dataclass
class Box:
    id: str
    x: float
    y: float
    w: float
    h: float
    kind: str
    payload: dict[str, Any]

    def to_dict(self):
        return asdict(self)


@dataclass
class LayoutResult:
    width: int
    height: int
    boxes: list[Box]
    section_bounds: dict[str, tuple[float, float, float, float]]

    def to_dict(self):
        return {
            "width": self.width,
            "height": self.height,
            "boxes": [b.to_dict() for b in self.boxes],
            "section_bounds": self.section_bounds,
        }


def _density_factor(density: str) -> float:
    return {"concise": 0.88, "balanced": 1.0, "detailed": 1.14}.get(density, 1.0)


def layout_diagram(spec: DiagramSpec, prefs: Preferences, width: int = 900, height: int = 1800) -> LayoutResult:
    boxes: list[Box] = []
    bounds: dict[str, tuple[float, float, float, float]] = {}
    left, right = 54, 846
    content_w = right - left
    y = 190
    header_h = 44
    density = _density_factor(prefs.density)
    spacing = prefs.spacing_scale

    remaining = height - 190 - 82
    weights = []
    for sec in spec.sections:
        n = max(1, len(sec.nodes))
        base = 1.0 + min(n, 6) * 0.12
        if any(node.children for node in sec.nodes):
            base += 0.35
        if sec.note:
            base += 0.15
        weights.append(base)
    unit = remaining / max(sum(weights), 1)

    for idx, (sec, wt) in enumerate(zip(spec.sections, weights), 1):
        sec_h = max(180, unit * wt * density)
        if y + sec_h > height - 60:
            sec_h = max(150, height - 60 - y)
        bounds[sec.id] = (left, y, content_w, sec_h)
        boxes.append(Box(f"section-{sec.id}", left, y, content_w, header_h, "section_header", {
            "index": idx, "title": sec.title, "title_en": sec.title_en, "color": sec.color
        }))
        inner_y = y + header_h + 16 * spacing
        inner_h = sec_h - header_h - 24 * spacing
        nodes = sec.nodes
        n = len(nodes)
        if n:
            if n == 1:
                cols = 1
            elif n <= 3:
                cols = n
            elif n <= 6:
                cols = 3
            else:
                cols = 4
            rows = (n + cols - 1) // cols
            gap_x = 16 * spacing
            gap_y = 14 * spacing
            if sec.note:
                note_h = 38
                node_area_h = max(70, inner_h - note_h - gap_y)
            else:
                note_h = 0
                node_area_h = inner_h
            node_w = (content_w - (cols - 1) * gap_x) / cols
            node_h = (node_area_h - (rows - 1) * gap_y) / rows
            for i, node in enumerate(nodes):
                r, c = divmod(i, cols)
                x = left + c * (node_w + gap_x)
                ny = inner_y + r * (node_h + gap_y)
                boxes.append(Box(node.id, x, ny, node_w, node_h, "node", node.to_dict()))
                if node.children:
                    child_gap = 10 * spacing
                    child_cols = min(3, len(node.children))
                    child_w = (node_w - 20 - (child_cols-1)*child_gap) / child_cols
                    child_y = ny + node_h * 0.52
                    child_h = max(36, node_h * 0.36)
                    for j, child in enumerate(node.children[:child_cols]):
                        cx = x + 10 + j*(child_w+child_gap)
                        boxes.append(Box(child.id, cx, child_y, child_w, child_h, "child_node", child.to_dict()))
            if sec.note:
                boxes.append(Box(f"note-{sec.id}", left, inner_y + node_area_h + gap_y, content_w, note_h, "note", {"text": sec.note, "color": sec.color}))
        y += sec_h + 12 * spacing
    return LayoutResult(width, height, boxes, bounds)
