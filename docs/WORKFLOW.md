# End-to-end workflow

```text
① Materials
   ↓
② Evidence inventory + semantic extraction
   ↓
③ Compact questionnaire + preset references
   ↓
④ project_model.json
   ↓
⑤ Project Architecture spec + Technical Architecture spec
   ↓
⑥ Layout engine
   ↓
⑦ SVG renderer
   ↓
⑧ QA → auto-fix → re-render (up to N rounds)
   ↓
⑨ PNG/PDF/A4 export
   ↓
⑩ interactive_editor.html + config/spec/model/source bundle
   ↓
⑪ Natural-language or browser-based tuning → re-layout → QA → re-export
```

## Agent orchestration

The agent owns project understanding and semantic editing. The local engine owns deterministic layout, vector rendering, quality checks, and export. This separation keeps the system both intelligent and reproducible.
