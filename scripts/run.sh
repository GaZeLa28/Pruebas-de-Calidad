#!/usr/bin/env bash
set -euo pipefail

[ -f .env ] || { echo "No existe .env." >&2; exit 1; }
[ -d .venv ] || { echo "No existe .venv. Ejecute scripts/install.sh." >&2; exit 1; }
source .venv/bin/activate
python manage.py runserver
