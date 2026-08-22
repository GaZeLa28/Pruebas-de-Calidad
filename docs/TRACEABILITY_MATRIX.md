# Matriz de trazabilidad de requerimientos

La solución reemplaza la tecnología ASP.NET indicada originalmente por Python 3.14, Django y Django REST Framework, conforme a la solicitud posterior del equipo. El alcance funcional, los actores, las historias de usuario y SQL Server se mantienen.

| Requerimiento | Implementación principal | API / interfaz | Evidencia de calidad |
|---|---|---|---|
| HU01 Inicio de sesión seguro | `apps.accounts` y autenticación Django | `/login/`, `POST /api/v1/auth/login/` | Hashers, CSRF, throttling y permisos |
| EDT 1.1.1.2 Recuperación de contraseña | `PasswordResetService` y vistas de autenticación | `/password-reset/`, endpoints REST de recuperación | Token temporal, validadores de contraseña e invalidación de tokens |
| HU02 Productores | `Producer`, `ProducerViewSet` | `/manage/producers/`, `/api/v1/producers/` | Código e identificación únicos, índices y auditoría |
| HU03 Fincas | `Farm`, `FarmViewSet` | `/manage/farms/`, `/api/v1/farms/` | Relación obligatoria con productor y unicidad por productor |
| HU04 Recepciones | `CoffeeReception`, `ReceptionService` | `/manage/receptions/`, `/api/v1/receptions/` | Transacción atómica y validación finca-productor |
| HU05 Pesos | `WeightValidationService` | Incluido en recepciones | Restricción bruto mayor que tara y cálculo decimal |
| HU06 Lotes | `Lot`, `LotService` | `/manage/lots/`, `/api/v1/lots/` | Totales recalculados transaccionalmente |
| HU07 Asociación de productores/lotes | `LotReception` | `POST /api/v1/lots/{id}/associate-reception/` | Solo recepciones validadas y límite de peso disponible |
| HU08 Historial del lote | `TraceabilitySelector` y timeline | `/lots/{id}/`, `/api/v1/traceability/lots/{id}/` | `select_related`/`prefetch_related` e integridad resumida |
| HU09 Consulta QR | `LotQRCode`, `QRCodeService` | `/qr/{token}/`, API pública por token | Token UUID activo y lectura sin efectos secundarios |
| HU10 Reporte por productor | `ReportQueryService` | JSON, Excel y PDF | Agregaciones en base de datos y filtros por fecha |
| HU11 Reporte por lote | `ReportQueryService` | JSON, Excel y PDF | Conteos distintos y filtro por cosecha |
| HU12 Usuarios y permisos | `UserProfile`, permisos DRF | `/api/v1/users/`, `/admin/` | Roles Administrador, Operador, Auditor y Consulta |
| HU13 Verificación de trazabilidad | Timeline autenticado y consulta pública | Detalle de lote y QR | Orígenes, eventos e indicador de integridad |
| HU14 Exportación | Renderizadores Excel/PDF | Endpoints `/export.xlsx` y `/export.pdf` | Clases especializadas sin lógica de consulta duplicada |
| HU15 Alertas de peso | `WeightInconsistency`, `InconsistencyService` | `/api/v1/weight-inconsistencies/` | Creación/actualización automática y resolución auditada |
| Auditoría | `AuditLog`, `AuditService` | `/api/v1/audit-logs/` | Actor, IP, objeto y valores antes/después; secretos redactados |

## Separación de responsabilidades

- **Modelos:** estructura e integridad persistente.
- **Serializadores:** contrato y validación de entrada/salida.
- **Servicios:** un caso de uso o regla de negocio por método.
- **Selectores:** consultas complejas y optimizadas.
- **Vistas/API:** adaptación HTTP y delegación.
- **Plantillas y JavaScript:** experiencia de usuario y presentación.
