# Revisión: conexión a SQL Server existente

## Objetivo

Adaptar CoffeeTrace para utilizar la base `CoffeeTrace` y el login `coffeetrace_app` creados previamente por el administrador, sin aprovisionamiento automático de infraestructura.

## Cambios realizados

1. Se eliminó el fallback de ejecución a SQLite.
2. Se retiró el script que creaba base, login y usuario.
3. Se agregó configuración orientada a objetos en `coffeetrace/config/`.
4. `DB_PASSWORD` es obligatorio y la aplicación falla de forma clara cuando falta.
5. Se agregó `python manage.py check_database`, de solo lectura.
6. Instalación, verificación, migración y arranque se separaron en scripts independientes.
7. Las migraciones ya no se ejecutan desde el script de arranque.
8. Se agregaron scripts SQL de verificación y administración temporal de `db_ddladmin`.
9. CI utiliza una base SQL Server aislada para pruebas, no la base operativa.
10. Se refactorizaron servicios de lotes, reportes y datos demo para reforzar responsabilidad única.
11. Se actualizaron dependencias para Python 3.14, Django y Django REST Framework.
12. Se mantuvieron los módulos del avance: usuarios, productores, fincas, recepciones, lotes, trazabilidad, QR, reportes y auditoría.

## Archivos principales

- `coffeetrace/config/environment.py`
- `coffeetrace/config/database.py`
- `coffeetrace/settings.py`
- `apps/common/database_health.py`
- `apps/common/management/commands/check_database.py`
- `.env.example`
- `scripts/check-db.ps1`
- `scripts/migrate.ps1`
- `scripts/run.ps1`
- `scripts/sql/001_verify_existing_database.sql`
