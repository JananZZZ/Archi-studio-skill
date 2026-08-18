from __future__ import annotations

from pathlib import Path
import re
from .models import ProjectModel, Evidence
from .utils import TEXT_EXTS, read_text_safe, compact

STACK_HINTS = {
    "frontend": ["react", "vue", "svelte", "angular", "next.js", "vite", "typescript", "javascript", "xterm"],
    "backend": ["flask", "fastapi", "django", "express", "nestjs", "spring", "rust", "tauri", "tokio", "python"],
    "data": ["sqlite", "postgres", "mysql", "redis", "mongodb", "rusqlite"],
    "delivery": ["docker", "pyinstaller", "github actions", "cargo", "pytest", "vitest", "playwright"],
}
READ_PRIORITIES = ["README.md", "README.zh.md", "README.en.md", "CLAUDE.md", "package.json", "pyproject.toml", "Cargo.toml", "requirements.txt"]
NOISY_DIRS = {"examples", "example", "tests", "test", "fixtures", "fixture", "samples", "sample", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}


def _is_noisy(p: Path, root: Path) -> bool:
    rel = p.relative_to(root)
    return any(part.lower() in NOISY_DIRS for part in rel.parts[:-1])


def _candidate_files(root: Path, max_files: int = 160) -> list[Path]:
    primary, secondary = [], []
    for name in READ_PRIORITIES:
        for p in root.rglob(name):
            if p.is_file() and not any(part.startswith(".") and part != ".github" for part in p.relative_to(root).parts[:-1]):
                (secondary if _is_noisy(p, root) else primary).append(p)
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in TEXT_EXTS and p not in primary and p not in secondary:
            rel = p.relative_to(root)
            if any(part.startswith(".") and part != ".github" for part in rel.parts[:-1]):
                continue
            (secondary if _is_noisy(p, root) else primary).append(p)
    def rank(p: Path):
        rel = p.relative_to(root)
        root_bonus = 0 if len(rel.parts) == 1 else 1
        try: pri = READ_PRIORITIES.index(p.name)
        except ValueError: pri = 99
        return (root_bonus, pri, len(rel.parts), str(rel).lower())
    return sorted(primary, key=rank)[:max_files] + sorted(secondary, key=rank)[:max(0, max_files-len(primary))]


def _project_name(root: Path, primary_corpus: str) -> str:
    m = re.search(r"^#\s+(.+)$", primary_corpus, re.M)
    if m:
        return compact(re.sub(r"[`*_#]", "", m.group(1)), 60)
    return root.name


def _extract_positioning(corpus: str) -> str:
    for pat in [r"(?:项目定位|定位|这是什么|What is this)[：:\s]*([^\n]{10,180})", r"^>\s*([^\n]{10,180})"]:
        m = re.search(pat, corpus, re.I | re.M)
        if m: return compact(m.group(1), 150)
    paragraphs = [compact(x, 150) for x in re.split(r"\n\s*\n", corpus) if 20 < len(x.strip()) < 300]
    return paragraphs[0] if paragraphs else ""


def _extract_bullets(corpus: str, keywords: list[str], limit: int = 8) -> list[str]:
    lines, out, active = [x.strip() for x in corpus.splitlines()], [], False
    for line in lines:
        if any(k.lower() in line.lower() for k in keywords) and (line.startswith("#") or len(line) < 80):
            active = True; continue
        if active and line.startswith("#"):
            if out: break
            active = False
        if active and re.match(r"^[-*+]\s+", line):
            out.append(compact(re.sub(r"\*\*|`", "", re.sub(r"^[-*+]\s+", "", line)), 100))
            if len(out) >= limit: break
    return out


def _contains_term(text: str, term: str) -> bool:
    # Avoid substring false positives (e.g. SSE inside assets). Punctuation in terms remains supported.
    return re.search(rf"(?<![A-Za-z0-9_]){re.escape(term)}(?![A-Za-z0-9_])", text, re.I) is not None


def _extract_stack(corpus: str) -> dict[str, list[str]]:
    display = {"react":"React","vue":"Vue","svelte":"Svelte","angular":"Angular","next.js":"Next.js","vite":"Vite","typescript":"TypeScript","javascript":"JavaScript","xterm":"xterm.js","flask":"Flask","fastapi":"FastAPI","django":"Django","express":"Express","nestjs":"NestJS","spring":"Spring","rust":"Rust","tauri":"Tauri","tokio":"Tokio","python":"Python","sqlite":"SQLite","postgres":"PostgreSQL","mysql":"MySQL","redis":"Redis","mongodb":"MongoDB","rusqlite":"rusqlite","docker":"Docker","pyinstaller":"PyInstaller","github actions":"GitHub Actions","cargo":"Cargo","pytest":"pytest","vitest":"Vitest","playwright":"Playwright"}
    stack = {}
    for layer, hints in STACK_HINTS.items():
        hits = []
        for term in hints:
            if _contains_term(corpus, term):
                name = display.get(term, term)
                if name not in hits: hits.append(name)
        if hits: stack[layer] = hits[:8]
    return stack


def analyze_project(path: str | Path) -> ProjectModel:
    root = Path(path).expanduser().resolve()
    if not root.exists(): raise FileNotFoundError(root)
    if root.is_file(): root = root.parent
    files = _candidate_files(root)
    primary_chunks, all_chunks, evidences = [], [], []
    for p in files:
        txt = read_text_safe(p, 80_000)
        if not txt: continue
        rel = str(p.relative_to(root)); chunk = f"\n\n--- FILE: {rel} ---\n{txt}"
        all_chunks.append(chunk)
        if not _is_noisy(p, root): primary_chunks.append(chunk)
        evidences.append(Evidence(source=rel, kind=p.suffix.lstrip(".") or "text", excerpt=compact(txt, 220), confidence=1.0 if not _is_noisy(p, root) else 0.65))
    primary_corpus = "".join(primary_chunks) or "".join(all_chunks)
    corpus = primary_corpus  # semantic facts come from authoritative corpus by default
    model = ProjectModel()
    model.name = _project_name(root, primary_corpus)
    model.positioning = _extract_positioning(corpus)
    model.capabilities = _extract_bullets(corpus, ["特性", "功能", "features", "capabilities"], 10)
    model.pain_points = _extract_bullets(corpus, ["痛点", "问题", "pain", "challenge"], 6)
    model.tech_stack = _extract_stack(corpus)
    model.quality_release = _extract_bullets(corpus, ["测试", "质量", "构建", "release", "test", "build"], 8)
    model.evidence = evidences[:50]
    modules = []
    for p in sorted(root.iterdir(), key=lambda x: x.name.lower()):
        if p.is_dir() and not p.name.startswith(".") and p.name.lower() not in NOISY_DIRS:
            modules.append({"name": p.name, "role": "代码/资源模块", "source": p.name})
        if len(modules) >= 9: break
    model.modules = modules
    evo = []
    for pattern in [r"(?im)^#+\s*(?:step\s*\d+|阶段\s*\d+)[^\n]*", r"(?im)^#+\s*([\w.-]+(?:-CC|-cc))\b[^\n]*"]:
        for m in re.finditer(pattern, corpus):
            label = compact(m.group(0).lstrip("# "), 80)
            if label and label not in [x.get("name") for x in evo]: evo.append({"name": label, "role": "演进阶段", "highlights": []})
            if len(evo) >= 5: break
    model.evolution = evo
    if not model.positioning: model.positioning = f"{model.name} 的项目与技术架构"
    if not model.capabilities: model.capabilities = [m["name"] for m in modules[:6]]
    return model
