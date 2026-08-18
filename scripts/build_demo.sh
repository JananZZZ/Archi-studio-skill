#!/usr/bin/env bash
set -euo pipefail
python -m archi_studio.cli build examples/sample_input --out examples/sample_output --non-interactive
