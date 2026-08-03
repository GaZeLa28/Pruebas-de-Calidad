from __future__ import annotations

from dataclasses import asdict, dataclass

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import DecimalField, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from decimal import Decimal

from apps.accounts.models import UserRole
from apps.accounts.permissions import get_role
from apps.audit.models import AuditLog
from apps.lots.models import Lot
from apps.producers.models import Farm, Producer
from apps.receptions.models import CoffeeReception, ReceptionStatus, WeightInconsistency
from apps.traceability.selectors import TraceabilitySelector
from apps.traceability.serializers import TraceabilityTimelineSerializer


@dataclass(frozen=True)
class ResourcePage:
    title: str
    eyebrow: str
    description: str
    api_url: str
    create_label: str
    columns: list[dict]
    fields: list[dict]
    search_placeholder: str


RESOURCE_PAGES = {
    "producers": ResourcePage(
        title="Productores",
        eyebrow="Origen del café",
        description="Administre la información de los productores afiliados a la cooperativa.",
        api_url="/api/v1/producers/",
        create_label="Nuevo productor",
        search_placeholder="Buscar por nombre, código o identificación…",
        columns=[
            {"key": "code", "label": "Código"},
            {"key": "full_name", "label": "Productor"},
            {"key": "national_id", "label": "Identificación"},
            {"key": "phone", "label": "Teléfono"},
            {"key": "farms_count", "label": "Fincas", "type": "number"},
            {"key": "is_active", "label": "Estado", "type": "boolean"},
        ],
        fields=[
            {"name": "code", "label": "Código", "type": "text", "required": True},
            {"name": "national_id", "label": "Identificación", "type": "text", "required": True},
            {"name": "full_name", "label": "Nombre completo", "type": "text", "required": True, "wide": True},
            {"name": "email", "label": "Correo", "type": "email"},
            {"name": "phone", "label": "Teléfono", "type": "text"},
            {"name": "address", "label": "Dirección", "type": "textarea", "wide": True},
            {"name": "is_active", "label": "Productor activo", "type": "checkbox", "default": True},
        ],
    ),
    "farms": ResourcePage(
        title="Fincas",
        eyebrow="Ubicación productiva",
        description="Registre las fincas y vincúlelas con su productor responsable.",
        api_url="/api/v1/farms/",
        create_label="Nueva finca",
        search_placeholder="Buscar finca, productor o ubicación…",
        columns=[
            {"key": "code", "label": "Código"},
            {"key": "name", "label": "Finca"},
            {"key": "producer_name", "label": "Productor"},
            {"key": "province", "label": "Provincia"},
            {"key": "canton", "label": "Cantón"},
            {"key": "altitude_masl", "label": "Altitud", "type": "number", "suffix": " m"},
            {"key": "is_active", "label": "Estado", "type": "boolean"},
        ],
        fields=[
            {"name": "producer", "label": "Productor", "type": "remote-select", "source": "/api/v1/producers/?is_active=true&page_size=100", "value": "id", "text": "full_name", "required": True},
            {"name": "code", "label": "Código", "type": "text", "required": True},
            {"name": "name", "label": "Nombre de la finca", "type": "text", "required": True, "wide": True},
            {"name": "province", "label": "Provincia", "type": "text", "required": True},
            {"name": "canton", "label": "Cantón", "type": "text", "required": True},
            {"name": "district", "label": "Distrito", "type": "text", "required": True},
            {"name": "address", "label": "Dirección exacta", "type": "textarea", "wide": True},
            {"name": "latitude", "label": "Latitud", "type": "number", "step": "0.000001"},
            {"name": "longitude", "label": "Longitud", "type": "number", "step": "0.000001"},
            {"name": "altitude_masl", "label": "Altitud (msnm)", "type": "number"},
            {"name": "area_hectares", "label": "Área (ha)", "type": "number", "step": "0.01"},
            {"name": "certification", "label": "Certificación", "type": "text"},
            {"name": "is_active", "label": "Finca activa", "type": "checkbox", "default": True},
        ],
    ),
    "receptions": ResourcePage(
        title="Recepciones",
        eyebrow="Ingreso de materia prima",
        description="Controle entregas, pesos y validaciones desde el punto de recepción.",
        api_url="/api/v1/receptions/",
        create_label="Registrar recepción",
        search_placeholder="Buscar código, productor, finca o variedad…",
        columns=[
            {"key": "code", "label": "Recepción"},
            {"key": "producer_name", "label": "Productor"},
            {"key": "farm_name", "label": "Finca"},
            {"key": "received_at", "label": "Fecha", "type": "datetime"},
            {"key": "calculated_net_weight_kg", "label": "Peso neto", "type": "decimal", "suffix": " kg"},
            {"key": "status_display", "label": "Validación", "type": "status"},
        ],
        fields=[
            {"name": "code", "label": "Código de recepción", "type": "text", "required": True},
            {"name": "received_at", "label": "Fecha y hora", "type": "datetime-local", "required": True, "default": "now"},
            {"name": "producer", "label": "Productor", "type": "remote-select", "source": "/api/v1/producers/?is_active=true&page_size=100", "value": "id", "text": "full_name", "required": True},
            {"name": "farm", "label": "Finca", "type": "remote-select", "source": "/api/v1/farms/?is_active=true&page_size=100", "value": "id", "text": "name", "required": True},
            {"name": "coffee_variety", "label": "Variedad", "type": "text", "required": True},
            {"name": "process_type", "label": "Proceso", "type": "text"},
            {"name": "gross_weight_kg", "label": "Peso bruto (kg)", "type": "number", "step": "0.01", "required": True},
            {"name": "tare_weight_kg", "label": "Tara (kg)", "type": "number", "step": "0.01", "required": True, "default": 0},
            {"name": "declared_net_weight_kg", "label": "Peso neto declarado (kg)", "type": "number", "step": "0.01", "required": True},
            {"name": "moisture_percentage", "label": "Humedad (%)", "type": "number", "step": "0.01"},
            {"name": "notes", "label": "Observaciones", "type": "textarea", "wide": True},
        ],
    ),
    "lots": ResourcePage(
        title="Lotes",
        eyebrow="Consolidación y seguimiento",
        description="Agrupe recepciones, controle el peso consolidado y genere códigos QR.",
        api_url="/api/v1/lots/",
        create_label="Crear lote",
        search_placeholder="Buscar código, lote, productor o recepción…",
        columns=[
            {"key": "code", "label": "Código"},
            {"key": "name", "label": "Lote"},
            {"key": "harvest_year", "label": "Cosecha", "type": "number"},
            {"key": "total_weight_kg", "label": "Peso total", "type": "decimal", "suffix": " kg"},
            {"key": "producers_count", "label": "Productores", "type": "number"},
            {"key": "status_display", "label": "Estado", "type": "status"},
            {"key": "id", "label": "Detalle", "type": "link", "path": "/lots/{value}/"},
        ],
        fields=[
            {"name": "code", "label": "Código de lote", "type": "text", "required": True},
            {"name": "name", "label": "Nombre", "type": "text", "required": True},
            {"name": "harvest_year", "label": "Año de cosecha", "type": "number", "required": True},
            {"name": "warehouse_location", "label": "Ubicación en bodega", "type": "text"},
            {"name": "status", "label": "Estado", "type": "select", "required": True, "options": [{"value": "DRAFT", "text": "Borrador"}, {"value": "IN_PROCESS", "text": "En proceso"}, {"value": "CERTIFIED", "text": "Certificado"}, {"value": "CLOSED", "text": "Cerrado"}]},
            {"name": "notes", "label": "Observaciones", "type": "textarea", "wide": True},
            {"name": "is_active", "label": "Lote activo", "type": "checkbox", "default": True},
        ],
    ),
    "events": ResourcePage(
        title="Eventos de trazabilidad",
        eyebrow="Cadena de custodia",
        description="Documente cada movimiento y proceso aplicado a un lote.",
        api_url="/api/v1/traceability-events/",
        create_label="Registrar evento",
        search_placeholder="Buscar por lote, recepción, ubicación o descripción…",
        columns=[
            {"key": "occurred_at", "label": "Fecha", "type": "datetime"},
            {"key": "lot_code", "label": "Lote"},
            {"key": "event_type_display", "label": "Evento", "type": "status"},
            {"key": "location", "label": "Ubicación"},
            {"key": "description", "label": "Descripción"},
            {"key": "recorded_by_name", "label": "Registrado por"},
        ],
        fields=[
            {"name": "lot", "label": "Lote", "type": "remote-select", "source": "/api/v1/lots/?page_size=100", "value": "id", "text": "code", "required": True},
            {"name": "reception", "label": "Recepción asociada (opcional)", "type": "remote-select", "source": "/api/v1/receptions/?page_size=100", "value": "id", "text": "code"},
            {"name": "event_type", "label": "Tipo de evento", "type": "select", "required": True, "options": [{"value": "RECEPTION", "text": "Recepción"}, {"value": "LOT_CREATED", "text": "Creación de lote"}, {"value": "ASSOCIATION", "text": "Asociación"}, {"value": "PROCESSING", "text": "Proceso productivo"}, {"value": "QUALITY", "text": "Control de calidad"}, {"value": "CERTIFICATION", "text": "Certificación"}, {"value": "DISPATCH", "text": "Despacho"}, {"value": "CORRECTION", "text": "Corrección"}]},
            {"name": "occurred_at", "label": "Fecha y hora", "type": "datetime-local", "required": True, "default": "now"},
            {"name": "location", "label": "Ubicación", "type": "text"},
            {"name": "description", "label": "Descripción", "type": "textarea", "required": True, "wide": True},
        ],
    ),
}


@login_required
def dashboard(request):
    current_year = timezone.localdate().year
    current_month = timezone.localdate().month
    reception_weight = CoffeeReception.objects.filter(
        received_at__year=current_year,
        received_at__month=current_month,
    ).aggregate(total=Coalesce(Sum("calculated_net_weight_kg"), Decimal("0.00"), output_field=DecimalField()))["total"]
    context = {
        "producer_count": Producer.objects.filter(is_active=True).count(),
        "farm_count": Farm.objects.filter(is_active=True).count(),
        "active_lot_count": Lot.objects.filter(is_active=True).exclude(status="CLOSED").count(),
        "open_inconsistency_count": WeightInconsistency.objects.filter(status="OPEN").count(),
        "validated_reception_count": CoffeeReception.objects.filter(status=ReceptionStatus.VALIDATED).count(),
        "reception_weight": reception_weight,
        "recent_receptions": CoffeeReception.objects.select_related("producer", "farm")[:6],
        "recent_lots": Lot.objects.select_related("created_by")[:5],
        "recent_activity": AuditLog.objects.select_related("actor")[:7],
    }
    return render(request, "frontend/dashboard.html", context)


@login_required
def resource_page(request, resource: str):
    page = asdict(get_object_or_404_page(resource))
    page["can_write"] = get_role(request.user) in {UserRole.ADMIN, UserRole.OPERATOR}
    return render(request, "frontend/resource.html", {"resource": page})


@login_required
def lot_detail(request, lot_id: int):
    lot = get_object_or_404(TraceabilitySelector.lot_timeline_queryset(), pk=lot_id)
    timeline = TraceabilityTimelineSerializer(lot).data
    return render(
        request,
        "frontend/lot_detail.html",
        {
            "lot": lot,
            "timeline": timeline,
            "origins": lot.reception_links.all(),
            "events": lot.traceability_events.all(),
        },
    )


@login_required
def reports_page(request):
    if get_role(request.user) not in {UserRole.ADMIN, UserRole.AUDITOR}:
        raise PermissionDenied("Se requiere el rol Administrador o Auditor.")
    return render(request, "frontend/reports.html")


def public_qr_page(request, token):
    lot = get_object_or_404(
        TraceabilitySelector.lot_timeline_queryset(),
        qr_code__token=token,
        qr_code__is_active=True,
    )
    timeline = TraceabilityTimelineSerializer(lot).data
    return render(
        request,
        "public/traceability.html",
        {
            "lot": lot,
            "timeline": timeline,
            "origins": lot.reception_links.all(),
            "events": lot.traceability_events.all(),
        },
    )


def get_object_or_404_page(resource: str) -> ResourcePage:
    page = RESOURCE_PAGES.get(resource)
    if page is None:
        from django.http import Http404

        raise Http404("Recurso no encontrado")
    return page
