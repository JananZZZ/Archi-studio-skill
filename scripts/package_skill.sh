#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$ROOT/dist/Archi-studio-skill.zip}"
mkdir -p "$(dirname "$OUT")"
python - "$ROOT" "$OUT" <<'PY'
from pathlib import Path
import sys, zipfile
root=Path(sys.argv[1]); out=Path(sys.argv[2])
ignore={'.git','.venv','__pycache__','.pytest_cache','dist'}
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in root.rglob('*'):
        if not p.is_file() or any(part in ignore for part in p.parts): continue
        z.write(p,p.relative_to(root.parent))
print(out)
PY
