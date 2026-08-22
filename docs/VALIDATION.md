# Registro de validación del paquete CoffeeTrace 2.0

## Validaciones completadas

Se ejecutaron en el ambiente de generación:

- Compilación sintáctica de todos los archivos Python mediante `compileall`.
- Validación sintáctica de todos los archivos JavaScript mediante `node --check`.
- Verificación AST de imports internos.
- Verificación de migraciones iniciales e índices definidos en modelos y migraciones.
- Verificación de nombres de rutas utilizados por las plantillas.
- Verificación de archivos obligatorios.
- Verificación de configuración exclusiva para SQL Server.
- Comprobación de que `settings.py` no contiene fallback a SQLite.
- Comprobación de que la aplicación no contiene instrucciones `CREATE DATABASE` o `CREATE LOGIN`.
- Revisión de funciones extensas; la lógica de negocio quedó dividida en servicios y métodos cohesionados.

Resultado del validador:

```text
[OK] Python/POO imports
[OK] Migraciones e índices
[OK] Rutas de plantillas
[OK] JavaScript
[OK] Archivos requeridos
[OK] SQL Server existente
```

## Validación de conexión incluida

El comando siguiente realiza una consulta de solo lectura:

```bash
python manage.py check_database
```

Muestra la base, servidor, login, usuario y permisos detectados. No crea ni modifica objetos.

## Límite del ambiente de generación

El ambiente utilizado para preparar la entrega dispone de Python 3.13, no de Python 3.14, y no tiene una instancia SQL Server ni ODBC Driver 18. La red del contenedor tampoco permitió instalar las dependencias desde PyPI. Por ello, no se afirma que se hayan ejecutado aquí las migraciones, la suite Django o la conexión real a la base del usuario.

## Validación obligatoria en la computadora del proyecto

Con Python 3.14, ODBC Driver 18 y SQL Server disponibles:

```powershell
.\scripts\install.ps1
.\scripts\check-db.ps1
.\scripts\migrate.ps1
.\.venv\Scripts\Activate.ps1
python manage.py check
python manage.py makemigrations --check --dry-run
ruff check .
pytest --cov=apps --cov=coffeetrace --cov-report=term-missing
python manage.py collectstatic --noinput
```

Después de migrar, ejecute en SSMS:

```text
scripts/sql/002_verify_django_objects.sql
```

La cobertura mínima del 80 %, el tiempo de respuesta menor a 3 segundos y la conexión real con SQL Server deben confirmarse antes del merge a `develop`.
