# Natural-language Tuning Prompt

Map user edits to structured operations, then re-layout and QA.

Examples:
- “更简洁 20%” → trim secondary body copy and optional nodes while preserving core evidence.
- “字大一点” → typography_scale +0.05, then reflow.
- “更适合简历” → mode=resume, density=concise, emphasize product evolution/results.
- “两个模块合并，但保留两层” → one section/parent node with two internal child-layer groups.
- “颜色高级一点” → portfolio-premium or lower saturation; keep contrast.
