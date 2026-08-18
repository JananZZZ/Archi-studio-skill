# Archi Studio Skill

Use this skill whenever a user wants to turn project materials into a polished **project architecture diagram + technical architecture diagram** and expects automated analysis, professional layout, vector output, and iterative tuning.

## Mandatory workflow
1. Ingest materials first. Prefer reading provided files/repositories over asking the user to restate facts.
2. Build an evidence-backed project model before drawing.
3. Ask a compact questionnaire (normally 3–7 single-choice questions) unless the user has already specified the equivalent preferences.
4. Show or reference style presets when useful.
5. Produce two separate diagram specifications: Project Architecture and Technical Architecture.
6. Render with code/vector graphics. Do **not** use generative image models for the architecture diagrams.
7. Run automatic layout/typography/color QA. Iterate until no critical overflow/overlap errors remain.
8. Export SVG first; derive PNG/PDF from the same SVG source.
9. Generate an interactive HTML editor and a machine-readable config/model package.
10. Preserve provenance: distinguish verified facts from inferred architecture choices.

## Default design target
- Chinese-first labels with necessary English/technical abbreviations.
- 1:2 portrait diagrams unless the user specifies another ratio.
- Professional, restrained palette with 1 primary accent and 3–5 semantic accents.
- Minimum readable body font; never solve density only by shrinking text.
- Prefer information reduction, reflow, height redistribution, and section merging before reducing font size.

## Interaction contract
Natural-language edits such as “更简洁一点 / 字大一点 / 合并这两个模块 / 更像作品集 / 技术细节少 20%” must map to explicit config/spec changes, then trigger re-layout + QA + re-export.

## Completion checklist
- Project model generated
- Questionnaire preferences recorded
- Two diagram specs generated
- SVGs rendered
- QA report generated
- PNG/PDF exported when renderer available
- Interactive editor generated
- Source/config bundled
