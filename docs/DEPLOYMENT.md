# Despliegue con una base SQL Server existente

## Condiciones previas

- Base `CoffeeTrace` creada.
- Login de servidor `coffeetrace_app` creado.
- Usuario de base asociado al login.
- Roles `db_datareader`, `db_datawriter` y temporalmente `db_ddladmin`.
- TCP/IP habilitado.
- ODBC Driver 18 instalado.

La aplicación no realiza estas tareas.

## Configuración

Copie `.env.example` a `.env` y configure como mínimo:

```env
DJANGO_SECRET_KEY=una-clave-larga-y-aleatoria
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=dominio.example
DJANGO_CSRF_TRUSTED_ORIGINS=https://dominio.example
DB_NAME=CoffeeTrace
DB_USER=coffeetrace_app
DB_PASSWORD=contraseña-real
DB_HOST=servidor-o-ip
DB_PORT=1433
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_ENCRYPT=True
DB_TRUST_SERVER_CERTIFICATE=False
```

En laboratorios con certificado local puede usarse `DB_TRUST_SERVER_CERTIFICATE=True`. En producción debe instalarse un certificado válido y usar `False`.

## Instalación

```bash
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py check_database
```

## Migraciones explícitas

```bash
python manage.py migrate
```

No están incluidas en el script de arranque. Si se retiró `db_ddladmin`, ejecute primero `scripts/sql/004_grant_ddladmin_before_migrations.sql` con una cuenta administrativa y, al terminar, `scripts/sql/003_revoke_ddladmin_after_migrations.sql`.

## Archivos estáticos y usuario inicial

```bash
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## Producción

- Utilizar Gunicorn/Uvicorn o un servidor ASGI/WSGI compatible.
- Colocar un proxy inverso con HTTPS.
- Mantener `DJANGO_DEBUG=False`.
- Guardar `.env` fuera del repositorio.
- Aplicar copias de seguridad de SQL Server.
- No utilizar la contraseña de ejemplo.
- Supervisar `/api/v1/health/`.
- Ejecutar migraciones durante una ventana controlada.
