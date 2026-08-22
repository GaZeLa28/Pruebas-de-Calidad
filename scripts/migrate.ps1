$ErrorActionPreference = "Stop"

if (-not (Test-Path ".env")) {
    throw "No existe .env. Configure la conexión antes de migrar."
}
if (-not (Test-Path ".venv")) {
    throw "No existe .venv. Ejecute scripts/install.ps1 primero."
}

& .\.venv\Scripts\Activate.ps1
python manage.py migrate
