# CoffeeTrace 2.0

Sistema web para la trazabilidad de materias primas de cooperativas cafetaleras. Esta versión fue preparada para conectarse **exclusivamente a una base de datos SQL Server existente** llamada `CoffeeTrace` mediante el login `coffeetrace_app`.

La aplicación no crea automáticamente la base de datos, el login ni el usuario de SQL Server; tampoco cambia a SQLite cuando falta una configuración. Las migraciones de Django se ejecutan únicamente mediante un comando explícito.

## Tecnologías

- Python 3.14.
- Django 6.0.7.
- Django REST Framework 3.17.1.
- SQL Server mediante `mssql-django` 1.7.4 y ODBC Driver 18.
- HTML5, CSS3 y JavaScript.
- OpenPyXL, ReportLab y QRCode para reportes y códigos QR.
- Pytest, Coverage, Ruff y GitHub Actions para calidad.

## Alcance funcional

| Módulo | Historias de usuario |
|---|---|
| Autenticación, recuperación, usuarios, roles y permisos | HU01 y HU12 |
| Productores y fincas | HU02 y HU03 |
| Recepciones, pesos e inconsistencias | HU04, HU05 y HU15 |
| Lotes y asociación de recepciones/productores | HU06 y HU07 |
| Historial y verificación de trazabilidad | HU08 y HU13 |
| Consulta pública mediante QR | HU09 |
| Reportes por productor/lote y exportación | HU10, HU11 y HU14 |
| Auditoría de operaciones críticas | Requisito transversal |

## Arquitectura

```text
Navegador / cliente REST
          │
          ├── Presentación: templates + CSS + JavaScript
          ├── API REST: ViewSets / APIViews + serializers
          ├── Aplicación: servicios + selectores + permisos
          ├── Dominio: modelos y reglas de negocio
          └── Persistencia: Django ORM + SQL Server existente
```

La lógica no se coloca en plantillas ni se mezcla con el acceso a datos. Las vistas coordinan solicitudes; los serializers validan contratos; los servicios ejecutan una operación de negocio; los selectores concentran consultas optimizadas; y los modelos representan el dominio.

## Conexión configurada

El archivo local `.env` incluido en la entrega está preparado con estos valores:

```env
DB_NAME=CoffeeTrace
DB_USER=coffeetrace_app
DB_PASSWORD=ChangeMe_Strong_2026!
DB_HOST=localhost
DB_PORT=1433
DB_DRIVER=ODBC Driver 18 for SQL Server
```

`.env` está ignorado por Git. Cambie la contraseña tanto en SQL Server como en `.env` antes de utilizar la aplicación fuera de un laboratorio.

Cuando SQL Server Express utiliza una instancia con nombre, puede usar una de estas opciones:

```env
DB_HOST=localhost\SQLEXPRESS
DB_PORT=
```

O habilitar TCP/IP, fijar el puerto 1433 y mantener la configuración entregada.

## Instalación en Windows

### 1. Requisitos

1. Python 3.14 de 64 bits.
2. SQL Server Express, Developer o superior.
3. ODBC Driver 18 for SQL Server.
4. TCP/IP habilitado para la instancia de SQL Server.
5. La base `CoffeeTrace` y el usuario `coffeetrace_app` ya creados con el script proporcionado.

### 2. Instalar dependencias

Desde PowerShell, en la raíz del proyecto:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\install.ps1
```

Este script solamente crea el entorno virtual e instala dependencias. No toca la base de datos.

### 3. Verificar la conexión existente

```powershell
.\scripts\check-db.ps1
```

También puede ejecutar:

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py check_database
```

El comando es de solo lectura y muestra servidor, base, login, usuario y permisos detectados.

### 4. Crear las tablas de la aplicación dentro de `CoffeeTrace`

La base ya existe, pero Django necesita crear sus tablas. Esta acción es explícita:

```powershell
.\scripts\migrate.ps1
```

El comando `migrate` no crea otra base de datos: aplica las migraciones en `CoffeeTrace` usando la conexión definida en `.env`.

### 5. Crear el administrador

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py createsuperuser
```

Opcionalmente, para cargar datos académicos de demostración:

```powershell
python manage.py seed_demo --admin-password "UnaClaveSegura2026!"
```

### 6. Iniciar la plataforma

```powershell
.\scripts\run.ps1
```

Abra `http://127.0.0.1:8000/`.

## Separación de acciones

Los scripts fueron divididos para evitar automatizaciones ocultas:

| Script | Única responsabilidad |
|---|---|
| `scripts/install.ps1` | Crear entorno e instalar paquetes |
| `scripts/check-db.ps1` | Verificar conexión y permisos |
| `scripts/migrate.ps1` | Aplicar migraciones solicitadas por el usuario |
| `scripts/run.ps1` | Iniciar el servidor de desarrollo |

No existe ningún script de creación automática de base de datos o login.

## API REST

Base: `/api/v1/`

| Método y ruta | Función |
|---|---|
| `POST /api/v1/auth/login/` | Obtener token |
| `POST /api/v1/auth/logout/` | Revocar token |
| `GET /api/v1/auth/me/` | Usuario actual |
| `GET/POST /api/v1/producers/` | Productores |
| `GET/POST /api/v1/farms/` | Fincas |
| `GET/POST /api/v1/receptions/` | Recepciones |
| `GET/POST /api/v1/lots/` | Lotes |
| `GET/POST /api/v1/traceability-events/` | Eventos |
| `GET /api/v1/traceability/lots/{id}/` | Historial completo |
| `GET /api/v1/traceability/qr/{token}/` | Trazabilidad pública QR |
| `GET /api/v1/reports/producers/` | Reporte por productor |
| `GET /api/v1/reports/lots/` | Reporte por lote |
| `GET /api/v1/reports/producers/export.xlsx` | Exportación Excel por productor |
| `GET /api/v1/reports/lots/export.pdf` | Exportación PDF por lote |
| `GET /api/v1/audit-logs/` | Auditoría |
| `GET /api/v1/health/` | Salud de aplicación y SQL Server |

Esquema OpenAPI: `/api/schema/`.

Más detalle: [`docs/API.md`](docs/API.md).

## Seguridad y permisos de SQL Server

Durante el desarrollo y las migraciones, `coffeetrace_app` necesita `db_ddladmin`. Para una instalación estable puede retirarlo después de migrar:

```text
scripts/sql/003_revoke_ddladmin_after_migrations.sql
```

Antes de una migración futura, asígnelo temporalmente con:

```text
scripts/sql/004_grant_ddladmin_before_migrations.sql
```

La aplicación debe conservar `db_datareader` y `db_datawriter` para su operación normal.

## Calidad

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py check
python manage.py makemigrations --check --dry-run
ruff check .
pytest --cov=apps --cov=coffeetrace --cov-report=term-missing
```

Las pruebas de integración deben apuntar a una base SQL Server exclusiva para pruebas; nunca ejecute la suite destructiva contra la base de producción.

## Estructura

```text
apps/
  accounts/       autenticación, roles y usuarios
  producers/      productores y fincas
  receptions/     recepción, pesos e inconsistencias
  lots/           lotes, asociaciones y QR
  traceability/   eventos e historial
  reports/        reportes y exportaciones
  audit/          bitácora
  common/         componentes compartidos y diagnóstico SQL Server
  frontend/       páginas del sistema
coffeetrace/
  config/         lectura y validación de configuración
  settings.py     SQL Server obligatorio
scripts/
  sql/            verificación y permisos; no crea la base
static/            diseño UX/UI
  css/app.css
  js/
templates/         interfaz web responsiva
```

## Publicación en GitHub

El remoto esperado es:

```text
https://github.com/GaZeLa28/Pruebas-de-Calidad.git
```

Siga [`docs/PUBLISH_GITHUB.md`](docs/PUBLISH_GITHUB.md). El archivo `.env` no se publica porque está incluido en `.gitignore`.
