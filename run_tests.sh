#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if [ -x .venv/bin/python ]; then source .venv/bin/activate; fi
python -m pytest -q
if command -v node >/dev/null 2>&1; then node --check app/static/app.js; fi
