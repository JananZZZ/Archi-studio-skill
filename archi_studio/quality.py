from __future__ import annotations

from dataclasses import dataclass, asdict
from .layout import LayoutResult
from .models import Preferences


@dataclass
class Issue:
    severity: str
    code: str
    box_id: str
    message: str
    suggestion: str

    def to_dict(self):
        return asdict(self)


def _visual_units(text: str) -> float:
    return sum(1.0 if ord(ch) < 128 else 1.8 for ch in text)


def inspect(layout: LayoutResult, prefs: Preferences) -> list[Issue]:
    issues: list[Issue] = []
    for b in layout.boxes:
        if b.x < 0 or b.y < 0 or b.x + b.w > layout.width or b.y + b.h > layout.height:
            issues.append(Issue("critical", "OUT_OF_BOUNDS", b.id, "元素超出画布", "调整 section 高度或布局"))
        if b.kind in {"node", "child_node"}:
            payload = b.payload
            text = " ".join([payload.get("title", ""), payload.get("subtitle", ""), *payload.get("body", [])])
            approx_lines = max(1.0, _visual_units(text) / max(10, b.w / 8.0))
            usable_lines = max(1.0, b.h / (18 * prefs.typography_scale))
            if approx_lines > usable_lines * 1.35:
                issues.append(Issue("warning", "TEXT_DENSITY", b.id, "文本密度偏高", "精简文案、增加高度或重新分列"))
            if b.h < 48:
                issues.append(Issue("warning", "SMALL_BOX", b.id, "模块高度偏小", "增加 section 高度或减少行数"))
    # naive overlap check among same-level node boxes
    nodes = [x for x in layout.boxes if x.kind in {"node", "child_node"}]
    for i, a in enumerate(nodes):
        for b in nodes[i+1:]:
            if a.id.startswith("section") or b.id.startswith("section"):
                continue
            if max(a.x,b.x) < min(a.x+a.w,b.x+b.w) and max(a.y,b.y) < min(a.y+a.h,b.y+b.h):
                # child node inside parent is intentional
                if a.kind == "node" and b.kind == "child_node" and b.x >= a.x and b.x+b.w <= a.x+a.w and b.y >= a.y and b.y+b.h <= a.y+a.h:
                    continue
                if b.kind == "node" and a.kind == "child_node" and a.x >= b.x and a.x+a.w <= b.x+b.w and a.y >= b.y and a.y+a.h <= b.y+b.h:
                    continue
                issues.append(Issue("critical", "OVERLAP", f"{a.id}|{b.id}", "模块发生重叠", "重新布局或增加间距"))
    return issues


def auto_adjust(prefs: Preferences, issues: list[Issue]) -> Preferences:
    critical = [x for x in issues if x.severity == "critical"]
    density = [x for x in issues if x.code == "TEXT_DENSITY"]
    if critical:
        prefs.spacing_scale = max(0.85, prefs.spacing_scale * 0.95)
    if len(density) >= 3:
        prefs.typography_scale = max(0.9, prefs.typography_scale * 0.96)
    return prefs
