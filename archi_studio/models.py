from __future__ import annotations

from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any
import json


@dataclass
class Evidence:
    source: str
    kind: str
    excerpt: str
    confidence: float = 1.0


@dataclass
class ProjectModel:
    name: str = "Untitled Project"
    positioning: str = ""
    target_users: list[str] = field(default_factory=list)
    pain_points: list[str] = field(default_factory=list)
    evolution: list[dict[str, Any]] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    tech_stack: dict[str, list[str]] = field(default_factory=dict)
    modules: list[dict[str, Any]] = field(default_factory=list)
    flows: list[dict[str, Any]] = field(default_factory=list)
    quality_release: list[str] = field(default_factory=list)
    lifecycle: list[str] = field(default_factory=lambda: [
        "需求分析", "产品设计", "全栈开发", "测试发布", "开源运营"
    ])
    evidence: list[Evidence] = field(default_factory=list)
    inferred_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "ProjectModel":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        data["evidence"] = [Evidence(**x) for x in data.get("evidence", [])]
        return cls(**data)


@dataclass
class Preferences:
    mode: str = "portfolio"
    density: str = "balanced"
    language: str = "zh+en"
    palette: str = "portfolio-premium"
    emphasis: str = "balanced"
    interactive_editor: bool = True
    aspect_ratio: str = "1:2"
    width_mm: float = 94.0
    height_mm: float = 188.0
    typography_scale: float = 1.0
    spacing_scale: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NodeSpec:
    id: str
    title: str
    subtitle: str = ""
    body: list[str] = field(default_factory=list)
    color: str = "blue"
    emphasis: int = 1
    children: list["NodeSpec"] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            **{k: v for k, v in asdict(self).items() if k != "children"},
            "children": [x.to_dict() for x in self.children],
        }


@dataclass
class SectionSpec:
    id: str
    title: str
    title_en: str
    color: str
    nodes: list[NodeSpec] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "title_en": self.title_en,
            "color": self.color,
            "nodes": [x.to_dict() for x in self.nodes],
            "note": self.note,
        }


@dataclass
class DiagramSpec:
    kind: str
    title: str
    subtitle: str
    sections: list[SectionSpec]

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "title": self.title,
            "subtitle": self.subtitle,
            "sections": [x.to_dict() for x in self.sections],
        }


def node_from_dict(data: dict[str, Any]) -> NodeSpec:
    return NodeSpec(
        id=data["id"], title=data.get("title", ""), subtitle=data.get("subtitle", ""),
        body=list(data.get("body", [])), color=data.get("color", "blue"),
        emphasis=int(data.get("emphasis", 1)),
        children=[node_from_dict(x) for x in data.get("children", [])],
    )


def section_from_dict(data: dict[str, Any]) -> SectionSpec:
    return SectionSpec(
        id=data["id"], title=data.get("title", ""), title_en=data.get("title_en", ""),
        color=data.get("color", "blue"), nodes=[node_from_dict(x) for x in data.get("nodes", [])],
        note=data.get("note", ""),
    )


def diagram_from_dict(data: dict[str, Any]) -> DiagramSpec:
    return DiagramSpec(
        kind=data["kind"], title=data.get("title", ""), subtitle=data.get("subtitle", ""),
        sections=[section_from_dict(x) for x in data.get("sections", [])],
    )
