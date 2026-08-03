# Estrategia de pruebas

## Regla principal

Las pruebas de integración deben usar una base SQL Server exclusiva para pruebas. No ejecute `pytest` apuntando a la base operativa `CoffeeTrace` porque Django crea y destruye una base de prueba.

## Ejecución local

Configure temporalmente variables para una instancia SQL Server de pruebas:

```powershell
$env:DB_NAME = "CoffeeTraceTest"
$env:DB_USER = "usuario_pruebas"
$env:DB_PASSWORD = "contraseña_pruebas"
pytest --cov=apps --cov=coffeetrace --cov-report=term-missing
```

## Capas de prueba

- Unitarias: servicios, validadores y reglas de negocio.
- Integración: ORM, relaciones, restricciones y API REST sobre SQL Server.
- Funcionales: flujos completos por historia de usuario.
- Seguridad: permisos, autenticación, roles y datos sensibles.
- Regresión: endpoints y exportadores.
- Integridad: pesos, asociaciones, trazabilidad y auditoría.
- UAT: validación con escenarios del backlog.

## Calidad automática

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
ruff check .
pytest --cov=apps --cov=coffeetrace --cov-report=term-missing
```

La meta de cobertura configurada es 80 %.
