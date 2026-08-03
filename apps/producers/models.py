from __future__ import annotations

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.common.models import ActiveModel, TimeStampedModel


class Producer(ActiveModel, TimeStampedModel):
    code = models.CharField(max_length=20, unique=True, db_index=True)
    national_id = models.CharField(max_length=30, unique=True, db_index=True)
    full_name = models.CharField(max_length=180, db_index=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=300, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_producers",
    )

    class Meta:
        ordering = ["full_name"]
        verbose_name = "productor"
        verbose_name_plural = "productores"
        indexes = [models.Index(fields=["is_active", "full_name"], name="producer_active_name_idx")]

    def __str__(self) -> str:
        return f"{self.code} - {self.full_name}"


class Farm(ActiveModel, TimeStampedModel):
    producer = models.ForeignKey(Producer, on_delete=models.PROTECT, related_name="farms")
    code = models.CharField(max_length=25, unique=True, db_index=True)
    name = models.CharField(max_length=160, db_index=True)
    province = models.CharField(max_length=80)
    canton = models.CharField(max_length=80)
    district = models.CharField(max_length=80)
    address = models.CharField(max_length=300, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    altitude_masl = models.PositiveIntegerField(null=True, blank=True)
    area_hectares = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
    )
    certification = models.CharField(max_length=120, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_farms",
    )

    class Meta:
        ordering = ["producer__full_name", "name"]
        verbose_name = "finca"
        verbose_name_plural = "fincas"
        constraints = [
            models.UniqueConstraint(fields=["producer", "name"], name="uq_farm_producer_name")
        ]
        indexes = [
            models.Index(fields=["producer", "is_active"], name="farm_producer_active_idx"),
            models.Index(fields=["province", "canton", "district"], name="farm_location_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"
