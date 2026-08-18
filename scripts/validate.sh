#!/usr/bin/env bash
set -euo pipefail
python -m pytest
rm -rf /tmp/archi-studio-validate
python -m archi_studio.cli build examples/sample_input --out /tmp/archi-studio-validate --non-interactive --no-raster
python - <<'PY'
import json
from pathlib import Path
p=Path('/tmp/archi-studio-validate/qa_report.json')
data=json.loads(p.read_text())
critical=sum(1 for issues in data.values() for x in issues if x['severity']=='critical')
assert critical == 0, data
print('validation passed')
PY
