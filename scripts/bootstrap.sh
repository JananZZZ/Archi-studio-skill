#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
python -m pip install -e '.[dev,render,yaml]'
echo 'Ready. Run: archi-studio init-demo'
