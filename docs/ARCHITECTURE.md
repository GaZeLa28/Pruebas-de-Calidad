# Arquitectura de CoffeeTrace 2.0

## Principios

La solución adopta un monolito modular con separación de responsabilidades, orientación a objetos y acceso exclusivo a una base SQL Server existente.

Principios aplicados:

- Responsabilidad única: cada método ejecuta una acción concreta.
- Separación entre presentación, aplicación, dominio y persistencia.
- Dependencias dirigidas hacia el dominio, no hacia la interfaz.
- Validación en serializers y servicios, no en JavaScript como única barrera.
- Consultas complejas encapsuladas en selectores.
- Operaciones de negocio críticas dentro de transacciones atómicas.
- Auditoría transversal sin exponer contraseñas ni tokens.
- Configuración SQL Server estricta y validada al iniciar Django.

## Capas

### Presentación

- Templates de Django.
- CSS responsivo y componentes reutilizables.
- JavaScript modular para consumo de la API.
- Vistas web delgadas que preparan contexto y delegan reglas.

### API REST

- `APIView` para operaciones específicas.
- `ModelViewSet` para recursos CRUD.
- Serializers para entrada, salida y validación contractual.
- Permisos por rol: administrador, operador, auditor y consulta.
- Respuestas paginadas y filtros de búsqueda/ordenamiento.

### Aplicación

- Services para casos de uso y transacciones.
- Selectors para consultas optimizadas con `select_related`, `prefetch_related`, agregaciones e índices.
- Clases de permisos para autorización.
- Servicio de diagnóstico SQL Server de solo lectura.

### Dominio

- Modelos Django para productores, fincas, recepciones, lotes, eventos, QR y auditoría.
- Restricciones, estados y validaciones de integridad.
- Métodos pequeños y cohesionados.

### Persistencia

- Django ORM.
- Backend `mssql-django`.
- Microsoft ODBC Driver 18.
- SQL Server `CoffeeTrace`, creado previamente por el administrador.

## Configuración de SQL Server

`coffeetrace/config/database.py` contiene `SqlServerConfiguration`, una clase inmutable que:

1. Lee variables mediante `Environment`.
2. Exige `DB_PASSWORD`.
3. Construye la configuración de Django.
4. Configura cifrado, timeout, reintentos y reutilización de conexiones.
5. No abre conexiones ni crea objetos.

`coffeetrace/settings.py` no contiene fallback a SQLite y no ejecuta SQL de aprovisionamiento.

## Flujo de una solicitud

```text
HTTP Request
    ↓
URL / Router
    ↓
View o ViewSet
    ↓
Serializer / Permission
    ↓
Service o Selector
    ↓
Model / Django ORM
    ↓
SQL Server CoffeeTrace
    ↓
Serializer / Template
    ↓
HTTP Response
```

## Organización modular

- `accounts`: usuarios, perfiles, roles, autenticación y recuperación.
- `producers`: productores y fincas.
- `receptions`: recepción, pesos e inconsistencias.
- `lots`: lotes, asociaciones y QR.
- `traceability`: historial y eventos.
- `reports`: reportes y exportaciones.
- `audit`: registro auditable.
- `common`: infraestructura común, paginación, errores y salud de base.
- `frontend`: páginas y configuración visual de recursos.

## Optimización

- Índices en códigos, estados, fechas y claves de consulta frecuentes.
- `select_related` para relaciones uno-a-uno y claves foráneas.
- `prefetch_related` para colecciones.
- Agregaciones realizadas en SQL Server.
- Paginación obligatoria para listados REST.
- `CONN_MAX_AGE` y `CONN_HEALTH_CHECKS` configurables.
- Timeouts de conexión y consulta.
- Transacciones atómicas en operaciones multiobjeto.

## Base ya existente

La aplicación distingue entre dos acciones:

- Aprovisionamiento de infraestructura: lo realiza el administrador con SQL Server Management Studio y está fuera del código de la aplicación.
- Creación/evolución de tablas de Django: se realiza manualmente con `python manage.py migrate` dentro de la base existente.

No se ejecutan migraciones al iniciar el servidor.
