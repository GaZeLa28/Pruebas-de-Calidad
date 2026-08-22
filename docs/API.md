# API REST de CoffeeTrace

## Autenticación

### Obtener token

`POST /api/v1/auth/login/`

```json
{
  "username": "admin",
  "password": "UnaClaveSegura2026!"
}
```

Use el encabezado:

```http
Authorization: Token <token>
```

### Usuario actual

`GET /api/v1/auth/me/`

### Invalidar token

`POST /api/v1/auth/logout/`

### Solicitar recuperación de contraseña

`POST /api/v1/auth/password-reset/`

```json
{
  "email": "usuario@cooperativa.cr"
}
```

La respuesta es deliberadamente genérica para no revelar si el correo está registrado.

### Confirmar recuperación de contraseña

`POST /api/v1/auth/password-reset-confirm/`

```json
{
  "uid": "MQ",
  "token": "token-temporal",
  "new_password": "UnaClaveNueva2026!"
}
```

Al completar el cambio se invalidan los tokens de API existentes del usuario.

### Estado del servicio

`GET /api/v1/health/`

Comprueba que la aplicación pueda ejecutar una consulta en la base de datos.

## Recursos

| Recurso | Endpoint | Métodos |
|---|---|---|
| Usuarios | `/api/v1/users/` | GET, POST, PUT, PATCH |
| Productores | `/api/v1/producers/` | GET, POST, PUT, PATCH |
| Fincas | `/api/v1/farms/` | GET, POST, PUT, PATCH |
| Recepciones | `/api/v1/receptions/` | GET, POST, PUT, PATCH |
| Inconsistencias | `/api/v1/weight-inconsistencies/` | GET |
| Lotes | `/api/v1/lots/` | GET, POST, PUT, PATCH |
| Eventos | `/api/v1/traceability-events/` | GET, POST, PUT, PATCH |
| Auditoría | `/api/v1/audit-logs/` | GET |

## Acciones de dominio

### Resolver inconsistencia

`POST /api/v1/weight-inconsistencies/{id}/resolve/`

```json
{
  "resolution_notes": "Se verificó la báscula y se corrigió el registro."
}
```

### Asociar recepción a lote

`POST /api/v1/lots/{lot_id}/associate-reception/`

```json
{
  "reception_id": 10,
  "assigned_weight_kg": "450.25"
}
```

### Retirar asociación

`POST /api/v1/lots/{lot_id}/receptions/{link_id}/remove/`

### Generar o reactivar QR

`POST /api/v1/lots/{lot_id}/generate-qr/`

### Imagen QR

`GET /api/v1/lots/{lot_id}/qr-image/`

Requiere que el QR haya sido generado previamente mediante la acción `generate-qr`. La lectura no crea registros ni produce efectos secundarios.

### Historial completo del lote

`GET /api/v1/traceability/lots/{lot_id}/`

### Historial público por QR

`GET /api/v1/traceability/qr/{token}/`

No requiere autenticación. Solo funciona para tokens activos.

## Reportes

| Reporte | JSON | Excel | PDF |
|---|---|---|---|
| Por productor | `/api/v1/reports/producers/` | `/api/v1/reports/producers/export.xlsx` | `/api/v1/reports/producers/export.pdf` |
| Por lote | `/api/v1/reports/lots/` | `/api/v1/reports/lots/export.xlsx` | `/api/v1/reports/lots/export.pdf` |

Filtros:

- Productores: `start_date`, `end_date`.
- Lotes: `harvest_year`.

## Respuestas de error

```json
{
  "success": false,
  "status_code": 400,
  "errors": {
    "farm": ["La finca seleccionada no pertenece al productor."]
  }
}
```

## Roles

| Acción | Administrador | Operador | Auditor | Consulta |
|---|:---:|:---:|:---:|:---:|
| Lectura operativa | Sí | Sí | Sí | Sí |
| Crear/editar operación | Sí | Sí | No | No |
| Usuarios y permisos | Sí | No | No | No |
| Reportes y auditoría | Sí | No | Sí | No |
