from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def python_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.py")
        if not any(part in {".git", ".venv", "__pycache__", "staticfiles"} for part in path.parts)
    )


def module_exists(module: str) -> bool:
    if not module.startswith(("apps.", "coffeetrace")):
        return True
    path = ROOT.joinpath(*module.split("."))
    return path.with_suffix(".py").exists() or (path / "__init__.py").exists()


def validate_python() -> list[str]:
    errors: list[str] = []
    for path in python_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as error:
            errors.append(f"{path.relative_to(ROOT)}: {error}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and not module_exists(node.module):
                errors.append(f"{path.relative_to(ROOT)}: módulo interno inexistente {node.module}")
    return errors


def validate_migrations() -> list[str]:
    errors: list[str] = []
    apps_with_models = [
        path.parent for path in ROOT.glob("apps/*/models.py") if path.parent.name not in {"common"}
    ]
    for app in apps_with_models:
        migrations = app / "migrations"
        if not migrations.exists() or not (migrations / "__init__.py").exists():
            errors.append(f"{app.relative_to(ROOT)}: falta el paquete migrations")
        elif not list(migrations.glob("0*.py")):
            errors.append(f"{app.relative_to(ROOT)}: falta migración inicial")

    expected_index_names = {
        "producer_active_name_idx",
        "farm_producer_active_idx",
        "farm_location_idx",
        "reception_prod_date_idx",
        "reception_farm_date_idx",
        "weight_inc_status_idx",
        "lot_harvest_status_idx",
        "lotrec_reception_lot_idx",
        "trace_lot_date_idx",
        "trace_type_date_idx",
        "audit_log_resource_idx",
    }
    model_text = "\n".join(
        path.read_text(encoding="utf-8") for path in ROOT.glob("apps/*/models.py")
    )
    migration_text = "\n".join(
        path.read_text(encoding="utf-8") for path in ROOT.glob("apps/*/migrations/0*.py")
    )
    for name in sorted(expected_index_names):
        if name not in model_text:
            errors.append(f"Índice {name}: no aparece en modelos")
        if name not in migration_text:
            errors.append(f"Índice {name}: no aparece en migraciones")
    return errors


def validate_templates() -> list[str]:
    errors: list[str] = []
    url_names = set(
        re.findall(
            r'name=["\']([^"\']+)["\']',
            "\n".join(path.read_text(encoding="utf-8") for path in ROOT.rglob("urls.py")),
        )
    )
    router_names = {
        "producer-list",
        "lot-qr-image",
    }
    url_names.update(router_names)
    for path in ROOT.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        for name in re.findall(r"{%\s*url\s+['\"]([^'\"]+)['\"]", text):
            if name not in url_names:
                errors.append(f"{path.relative_to(ROOT)}: URL no encontrada {name}")
    return errors


def validate_javascript() -> list[str]:
    errors: list[str] = []
    for path in sorted((ROOT / "static" / "js").glob("*.js")):
        process = subprocess.run(
            ["node", "--check", str(path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if process.returncode:
            errors.append(f"{path.relative_to(ROOT)}: {process.stderr.strip()}")
    return errors


def validate_required_files() -> list[str]:
    required = [
        "README.md",
        ".env.example",
        "requirements.txt",
        "manage.py",
        "docs/API.md",
        "docs/ARCHITECTURE.md",
        "docs/TRACEABILITY_MATRIX.md",
        "scripts/sql/001_verify_existing_database.sql",
        "templates/frontend/dashboard.html",
        "static/css/app.css",
    ]
    return [f"Falta {item}" for item in required if not (ROOT / item).exists()]


def validate_database_configuration() -> list[str]:
    errors: list[str] = []
    settings_text = (ROOT / "coffeetrace" / "settings.py").read_text(encoding="utf-8")
    database_text = (ROOT / "coffeetrace" / "config" / "database.py").read_text(encoding="utf-8")
    repository_text = settings_text + "\n" + database_text

    forbidden_patterns = {
        "django.db.backends.sqlite3": "No debe existir fallback automático a SQLite",
        "CREATE DATABASE": "La aplicación no debe crear la base de datos",
        "CREATE LOGIN": "La aplicación no debe crear logins",
    }
    for pattern, message in forbidden_patterns.items():
        if pattern in repository_text:
            errors.append(message)

    required_patterns = [
        '"ENGINE": "mssql"',
        'Environment.require("DB_PASSWORD")',
        "SqlServerConfiguration.from_environment()",
    ]
    for pattern in required_patterns:
        if pattern not in repository_text:
            errors.append(f"Falta configuración SQL Server obligatoria: {pattern}")
    return errors


def main() -> int:
    checks = {
        "Python/POO imports": validate_python(),
        "Migraciones e índices": validate_migrations(),
        "Rutas de plantillas": validate_templates(),
        "JavaScript": validate_javascript(),
        "Archivos requeridos": validate_required_files(),
        "SQL Server existente": validate_database_configuration(),
    }
    failed = False
    for name, errors in checks.items():
        if errors:
            failed = True
            print(f"[FAIL] {name}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"[OK] {name}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
