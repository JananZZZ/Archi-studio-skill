from __future__ import annotations

from pathlib import Path
import json
import re
import shutil
import subprocess
import textwrap

TEXT_EXTS = {
    ".md", ".txt", ".rst", ".py", ".js", ".ts", ".tsx", ".jsx", ".json",
    ".toml", ".yaml", ".yml", ".rs", ".go", ".java", ".kt", ".cs", ".sh",
    ".ps1", ".html", ".css", ".scss", ".xml", ".ini", ".cfg"
}


def read_text_safe(path: Path, max_chars: int = 200_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
    except Exception:
        return ""


def compact(text: str, limit: int = 120) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    return text if len(text) <= limit else text[: max(1, limit - 1)].rstrip() + "…"


def wrap_text(text: str, width: int) -> list[str]:
    if not text:
        return []
    if any("\u4e00" <= ch <= "\u9fff" for ch in text):
        # CJK-aware simple wrapping by visual units.
        lines, cur, units = [], "", 0
        for ch in text:
            u = 2 if "\u4e00" <= ch <= "\u9fff" else 1
            if units + u > width and cur:
                lines.append(cur)
                cur, units = ch, u
            else:
                cur += ch
                units += u
        if cur:
            lines.append(cur)
        return lines
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False) or [text]


def save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def which(cmd: str) -> str | None:
    return shutil.which(cmd)


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
