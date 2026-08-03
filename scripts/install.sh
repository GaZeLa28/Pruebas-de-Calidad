#!/usr/bin/env bash
set -euo pipefail

[ -d .venv ] || python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
