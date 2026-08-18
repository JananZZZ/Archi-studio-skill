from __future__ import annotations

from .models import ProjectModel, Preferences, DiagramSpec, SectionSpec, NodeSpec
from .utils import compact

COLORS = ["blue", "cyan", "orange", "purple", "green", "red", "slate"]


def _nodes_from_strings(prefix: str, items: list[str], color_cycle=True) -> list[NodeSpec]:
    out = []
    for i, item in enumerate(items):
        out.append(NodeSpec(id=f"{prefix}-{i+1}", title=compact(item, 48), color=COLORS[i % len(COLORS)] if color_cycle else "blue"))
    return out


def plan_project(model: ProjectModel, prefs: Preferences) -> DiagramSpec:
    pain = model.pain_points[:4] or ["部署 / 使用门槛", "配置复杂度", "状态可视性", "运行与资源管理"]
    positioning_nodes = [
        NodeSpec("positioning", "项目定位", body=[compact(model.positioning, 120)], color="blue", emphasis=2),
        NodeSpec("pain", "核心问题", body=pain, color="orange"),
    ]

    evolution_nodes = []
    if model.evolution:
        for i, stage in enumerate(model.evolution[:4]):
            evolution_nodes.append(NodeSpec(
                id=f"evo-{i+1}",
                title=stage.get("name", f"阶段 {i+1}"),
                subtitle=stage.get("role", "产品演进"),
                body=stage.get("highlights", [])[:2],
                color=["cyan", "orange", "purple", "green"][i % 4],
                emphasis=2,
            ))
    else:
        capabilities = model.capabilities[:6]
        if capabilities:
            for i, cap in enumerate(capabilities[:3]):
                evolution_nodes.append(NodeSpec(f"cap-evo-{i+1}", cap, subtitle=f"Stage {i+1}", color=["cyan","orange","purple"][i]))
        else:
            evolution_nodes = [
                NodeSpec("e1", "基础可用", subtitle="Make it work", color="cyan"),
                NodeSpec("e2", "体验优化", subtitle="Make it easy", color="orange"),
                NodeSpec("e3", "统一控制", subtitle="Make it controllable", color="purple"),
            ]

    capability_nodes = _nodes_from_strings("cap", model.capabilities[:6] or [m["name"] for m in model.modules[:6]])
    lifecycle_nodes = _nodes_from_strings("life", model.lifecycle[:5], color_cycle=True)

    sections = [
        SectionSpec("overview", "项目定位与核心问题", "PROJECT OVERVIEW", "blue", positioning_nodes),
        SectionSpec("evolution", "产品演进主线", "PRODUCT EVOLUTION", "purple", evolution_nodes, note="突出从可用 → 易用 → 可控的价值递进"),
        SectionSpec("capabilities", "代表能力与作品亮点", "KEY CAPABILITIES", "cyan", capability_nodes),
        SectionSpec("delivery", "独立交付闭环", "INDEPENDENT DELIVERY", "orange", lifecycle_nodes),
    ]
    if prefs.mode in {"resume", "portfolio"}:
        tags = ["产品化思维", "全栈开发", "自动化", "可视化", "工程交付"]
        sections.append(SectionSpec("tags", "简历 / 作品集关键词", "PORTFOLIO TAGS", "green", _nodes_from_strings("tag", tags)))
    return DiagramSpec("project", f"{model.name}｜项目架构图", "从项目问题、产品演进到交付能力的结构化表达", sections)


def plan_technical(model: ProjectModel, prefs: Preferences) -> DiagramSpec:
    stack_nodes = []
    for i, (layer, techs) in enumerate(model.tech_stack.items()):
        stack_nodes.append(NodeSpec(f"stack-{layer}", layer.title(), body=techs[:5], color=COLORS[i % len(COLORS)]))
    if not stack_nodes:
        stack_nodes = [NodeSpec("stack-generic", "Local Application", body=["UI / Service / Runtime / Data"], color="blue")]

    module_nodes = []
    for i, m in enumerate(model.modules[:6]):
        module_nodes.append(NodeSpec(f"module-{i+1}", m.get("name", f"Module {i+1}"), body=[m.get("role", "模块")], color=COLORS[i % len(COLORS)]))

    runtime_children = [
        NodeSpec("runtime-entry", "UI / Control Layer", body=["workspace / views / settings"], color="blue"),
        NodeSpec("runtime-core", "Runtime / Service Layer", body=["orchestration / tasks / diagnostics"], color="purple"),
        NodeSpec("runtime-exec", "Local Execution", body=["process / filesystem / storage"], color="green"),
    ]
    runtime = NodeSpec("runtime", "统一运行控制面", subtitle="Control Plane", body=["建议按前端控制层 + Runtime/本机执行层组织"], color="purple", emphasis=2, children=runtime_children)

    flow_items = []
    for flow in model.flows[:4]:
        flow_items.append(flow.get("name") or flow.get("flow") or str(flow))
    if not flow_items:
        flow_items = ["Input → Orchestration → Runtime", "Events → State → UI", "Tasks → Progress → Diagnostics"]

    quality = model.quality_release[:6] or ["Typecheck / Test", "Build / Package", "Release / Documentation"]

    sections = [
        SectionSpec("topology", "整体技术拓扑", "SYSTEM TOPOLOGY", "blue", stack_nodes),
        SectionSpec("modules", "应用与服务模块", "APPLICATION & SERVICES", "orange", module_nodes),
        SectionSpec("runtime", "运行时与本机执行", "RUNTIME & LOCAL EXECUTION", "purple", [runtime]),
        SectionSpec("flows", "关键数据 / 任务流", "KEY FLOWS", "green", _nodes_from_strings("flow", flow_items)),
        SectionSpec("quality", "工程质量与发布", "QUALITY & RELEASE", "orange", _nodes_from_strings("quality", quality)),
    ]
    return DiagramSpec("technical", f"{model.name}｜技术架构图", "保留关键技术、运行机制与工程链路，避免实现细枝末节淹没结构", sections)


def plan_dual(model: ProjectModel, prefs: Preferences) -> tuple[DiagramSpec, DiagramSpec]:
    return plan_project(model, prefs), plan_technical(model, prefs)
