from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel
from apps.lots.models import Lot
from apps.receptions.models import CoffeeReception


class TraceabilityEventType(models.TextChoices):
    RECEPTION = "RECEPTION", "Recepción"
    LOT_CREATED = "LOT_CREATED", "Creación de lote"
    ASSOCIATION = "ASSOCIATION", "Asociación de materia prima"
    PROCESSING = "PROCESSING", "Proceso productivo"
    QUALITY = "QUALITY", "Control de calidad"
    CERTIFICATION = "CERTIFICATION", "Certificación"
    DISPATCH = "DISPATCH", "Despacho"
    CORRECTION = "CORRECTION", "Corrección"


class TraceabilityEvent(TimeStampedModel):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name="traceability_events")
    reception = models.ForeignKey(
        CoffeeReception,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="traceability_events",
    )
    event_type = models.CharField(max_length=30, choices=TraceabilityEventType.choices, db_index=True)
    occurred_at = models.DateTimeField(db_index=True)
    location = models.CharField(max_length=180, blank=True)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recorded_traceability_events",
    )

    class Meta:
        ordering = ["occurred_at", "created_at"]
        verbose_name = "evento de trazabilidad"
        verbose_name_plural = "eventos de trazabilidad"
        indexes = [
            models.Index(fields=["lot", "occurred_at"], name="trace_lot_date_idx"),
            models.Index(fields=["event_type", "occurred_at"], name="trace_type_date_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.lot.code} - {self.get_event_type_display()}"
