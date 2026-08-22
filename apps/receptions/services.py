from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.receptions.models import (
    CoffeeReception,
    ReceptionStatus,
    WeightInconsistency,
    WeightInconsistencyStatus,
)


class WeightValidationService:
    @staticmethod
    def calculate_net(*, gross_weight: Decimal, tare_weight: Decimal) -> Decimal:
        net_weight = gross_weight - tare_weight
        if net_weight <= 0:
            raise ValidationError({"gross_weight_kg": "El peso bruto debe ser mayor que la tara."})
        return net_weight.quantize(Decimal("0.01"))

    @staticmethod
    def tolerance() -> Decimal:
        return Decimal(str(settings.WEIGHT_TOLERANCE_KG))

    @classmethod
    def is_consistent(cls, *, declared_weight: Decimal, calculated_weight: Decimal) -> bool:
        return abs(declared_weight - calculated_weight) <= cls.tolerance()


class ReceptionService:
    @staticmethod
    @transaction.atomic
    def create(*, actor, validated_data: dict) -> CoffeeReception:
        data = validated_data.copy()
        ReceptionService._validate_farm_owner(data)
        calculated = WeightValidationService.calculate_net(
            gross_weight=data["gross_weight_kg"],
            tare_weight=data.get("tare_weight_kg", Decimal("0")),
        )
        declared = data.pop("declared_net_weight_kg", calculated)
        status = (
            ReceptionStatus.VALIDATED
            if WeightValidationService.is_consistent(
                declared_weight=declared,
                calculated_weight=calculated,
            )
            else ReceptionStatus.INCONSISTENT
        )
        reception = CoffeeReception.objects.create(
            **data,
            declared_net_weight_kg=declared,
            calculated_net_weight_kg=calculated,
            status=status,
            received_by=actor,
        )
        InconsistencyService.sync_for_reception(reception)
        return reception

    @staticmethod
    @transaction.atomic
    def update(*, reception: CoffeeReception, validated_data: dict) -> CoffeeReception:
        data = validated_data.copy()
        producer = data.get("producer", reception.producer)
        farm = data.get("farm", reception.farm)
        ReceptionService._validate_farm_owner({"producer": producer, "farm": farm})
        for field, value in data.items():
            setattr(reception, field, value)
        reception.calculated_net_weight_kg = WeightValidationService.calculate_net(
            gross_weight=reception.gross_weight_kg,
            tare_weight=reception.tare_weight_kg,
        )
        reception.status = (
            ReceptionStatus.VALIDATED
            if WeightValidationService.is_consistent(
                declared_weight=reception.declared_net_weight_kg,
                calculated_weight=reception.calculated_net_weight_kg,
            )
            else ReceptionStatus.INCONSISTENT
        )
        ReceptionService._validate_existing_lot_assignments(reception)
        reception.save()
        InconsistencyService.sync_for_reception(reception)
        return reception

    @staticmethod
    def _validate_existing_lot_assignments(reception: CoffeeReception) -> None:
        assigned_weight = reception.lot_links.aggregate(
            total=Coalesce(Sum("assigned_weight_kg"), Decimal("0.00"))
        )["total"]
        if assigned_weight > reception.calculated_net_weight_kg:
            raise ValidationError(
                {
                    "gross_weight_kg": (
                        "El nuevo peso neto es menor que el peso ya asignado a lotes "
                        f"({assigned_weight} kg)."
                    )
                }
            )
        if assigned_weight > 0 and reception.status == ReceptionStatus.INCONSISTENT:
            raise ValidationError(
                {
                    "declared_net_weight_kg": (
                        "Una recepción asociada a un lote debe conservar pesos validados."
                    )
                }
            )

    @staticmethod
    def _validate_farm_owner(data: dict) -> None:
        farm = data.get("farm")
        producer = data.get("producer")
        if farm and producer and farm.producer_id != producer.id:
            raise ValidationError({"farm": "La finca seleccionada no pertenece al productor."})


class InconsistencyService:
    @staticmethod
    def sync_for_reception(reception: CoffeeReception) -> WeightInconsistency | None:
        difference = abs(reception.declared_net_weight_kg - reception.calculated_net_weight_kg)
        open_item = reception.weight_inconsistencies.filter(
            status=WeightInconsistencyStatus.OPEN
        ).first()
        if reception.status == ReceptionStatus.INCONSISTENT:
            description = (
                f"Diferencia de {difference} kg; tolerancia permitida: "
                f"{WeightValidationService.tolerance()} kg."
            )
            if open_item:
                open_item.difference_kg = difference
                open_item.description = description
                open_item.save(update_fields=["difference_kg", "description", "updated_at"])
                return open_item
            return WeightInconsistency.objects.create(
                reception=reception,
                difference_kg=difference,
                description=description,
            )
        if open_item:
            open_item.status = WeightInconsistencyStatus.RESOLVED
            open_item.resolution_notes = "Resuelta automáticamente tras corregir los pesos."
            open_item.resolved_at = timezone.now()
            open_item.save(
                update_fields=["status", "resolution_notes", "resolved_at", "updated_at"]
            )
        return None

    @staticmethod
    @transaction.atomic
    def resolve(*, inconsistency: WeightInconsistency, actor, notes: str) -> WeightInconsistency:
        if inconsistency.status == WeightInconsistencyStatus.RESOLVED:
            raise ValidationError("La inconsistencia ya se encuentra resuelta.")
        inconsistency.status = WeightInconsistencyStatus.RESOLVED
        inconsistency.resolved_by = actor
        inconsistency.resolution_notes = notes
        inconsistency.resolved_at = timezone.now()
        inconsistency.save()
        return inconsistency
