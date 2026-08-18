# Agent Integration Guide

## Recommended agent contract

1. Load `SYSTEM_PROMPT.md` as the high-level system behavior.
2. Load `SKILL.md` as the task workflow/acceptance contract.
3. When the user supplies project files or repositories, use available file/repository tools to build or enrich `project_model.json`.
4. Ask only unresolved preference questions.
5. Call the local engine to render deterministic artifacts.
6. Inspect `qa_report.json`; if critical issues remain, update specs/config and rebuild.
7. Present SVG/PDF/PNG + `interactive_editor.html` + source package.

## Recommended tool mapping

| Need | Agent capability |
|---|---|
| Read ZIP/project tree | Files / filesystem / container |
| Read GitHub repository | GitHub connector/API |
| Analyze code/docs | LLM + file reads |
| Generate semantic model | LLM structured output |
| Render diagrams | `python -m archi_studio.cli build ...` |
| Preview SVG/PNG | browser/image/file viewer |
| Iterate layout | edit JSON/config + rebuild |
| Deliver package | archive/zip + file handoff |

## Structured handoff

The agent should prefer modifying:
- `project_model.json` for factual/semantic changes,
- `diagram_specs.json` for architecture/story changes,
- `diagram.config.json` for visual changes.

The current reference engine generates those files from source on each clean build. In a production agent integration, load agent-refined versions into the corresponding dataclasses before layout/render.
