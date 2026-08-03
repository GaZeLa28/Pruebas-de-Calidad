from __future__ import annotations

import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import ActiveModel, TimeStampedModel
from apps.receptions.models import CoffeeReception


class LotStatus(models.TextChoices):
    DRAFT = "DRAFT", "Borrador"
    IN_PROCESS = "IN_PROCESS", "En proceso"
    CERTIFIED = "CERTIFIED", "Certificado"
    CLOSED = "CLOSED", "Cerrado"


class Lot(ActiveModel, TimeStampedModel):
    code = models.CharField(max_length=30, unique=True, db_index=True)
    name = models.CharField(max_length=160, db_index=True)
    harvest_year = models.PositiveSmallIntegerField(db_index=True)
    warehouse_location = models.CharField(max_length=160, blank=True)
    status = models.CharField(
        max_length=20,
        choices=LotStatus.choices,
        default=LotStatus.DRAFT,
        db_index=True,
    )
    total_weight_kg = models.DecimalField(
        max_digits=14, decimal_places=2, default=0, editable=False
    )
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_lots",
    )
    receptions = models.ManyToManyField(
        CoffeeReception,
        through="LotReception",
        related_name="lots",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "lote"
        verbose_name_plural = "lotes"
        indexes = [models.Index(fields=["harvest_year", "status"], name="lot_harvest_status_idx")]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class LotReception(TimeStampedModel):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE, related_name="reception_links")
    reception = models.ForeignKey(
        CoffeeReception,
        on_delete=models.PROTECT,
        related_name="lot_links",
    )
    assigned_weight_kg = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="lot_reception_assignments",
    )

    class Meta:
        ordering = ["created_at"]
        verbose_name = "recepción asociada al lote"
        verbose_name_plural = "recepciones asociadas al lote"
        constraints = [
            models.UniqueConstraint(fields=["lot", "reception"], name="uq_lot_reception"),
            models.CheckConstraint(
                condition=models.Q(assigned_weight_kg__gt=0),
                name="ck_lotrec_weight_pos",
            ),
        ]
        indexes = [models.Index(fields=["reception", "lot"], name="lotrec_reception_lot_idx")]

    def __str__(self) -> str:
        return f"{self.lot.code} ← {self.reception.code}"


class LotQRCode(TimeStampedModel):
    lot = models.OneToOneField(Lot, on_delete=models.CASCADE, related_name="qr_code")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="generated_lot_qr_codes",
    )

    class Meta:
        verbose_name = "código QR de lote"
        verbose_name_plural = "códigos QR de lotes"

    def __str__(self) -> str:
        return f"QR {self.lot.code}"
