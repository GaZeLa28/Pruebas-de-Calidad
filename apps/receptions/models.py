from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.common.models import TimeStampedModel
from apps.producers.models import Farm, Producer


class ReceptionStatus(models.TextChoices):
    PENDING = "PENDING", "Pendiente"
    VALIDATED = "VALIDATED", "Validada"
    INCONSISTENT = "INCONSISTENT", "Con inconsistencia"


class CoffeeReception(TimeStampedModel):
    code = models.CharField(max_length=30, unique=True, db_index=True)
    producer = models.ForeignKey(Producer, on_delete=models.PROTECT, related_name="receptions")
    farm = models.ForeignKey(Farm, on_delete=models.PROTECT, related_name="receptions")
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="coffee_receptions",
    )
    received_at = models.DateTimeField(db_index=True)
    coffee_variety = models.CharField(max_length=100)
    process_type = models.CharField(max_length=100, blank=True)
    gross_weight_kg = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    tare_weight_kg = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
    )
    declared_net_weight_kg = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
    )
    calculated_net_weight_kg = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    moisture_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    status = models.CharField(
        max_length=20,
        choices=ReceptionStatus.choices,
        default=ReceptionStatus.PENDING,
        db_index=True,
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-received_at"]
        verbose_name = "recepción de café"
        verbose_name_plural = "recepciones de café"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(gross_weight_kg__gt=models.F("tare_weight_kg")),
                name="ck_reception_gross_gt_tare",
            )
        ]
        indexes = [
            models.Index(fields=["producer", "received_at"], name="reception_prod_date_idx"),
            models.Index(fields=["farm", "received_at"], name="reception_farm_date_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.producer.full_name}"


class WeightInconsistencyStatus(models.TextChoices):
    OPEN = "OPEN", "Abierta"
    RESOLVED = "RESOLVED", "Resuelta"


class WeightInconsistency(TimeStampedModel):
    reception = models.ForeignKey(
        CoffeeReception,
        on_delete=models.CASCADE,
        related_name="weight_inconsistencies",
    )
    difference_kg = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=300)
    status = models.CharField(
        max_length=20,
        choices=WeightInconsistencyStatus.choices,
        default=WeightInconsistencyStatus.OPEN,
        db_index=True,
    )
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="resolved_weight_inconsistencies",
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "inconsistencia de peso"
        verbose_name_plural = "inconsistencias de peso"
        indexes = [models.Index(fields=["status", "created_at"], name="weight_inc_status_idx")]

    def __str__(self) -> str:
        return f"{self.reception.code} - {self.get_status_display()}"
