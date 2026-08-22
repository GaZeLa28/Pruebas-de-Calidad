from __future__ import annotations

from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.db.models.functions import Coalesce
from rest_framework.exceptions import ValidationError

from apps.lots.models import Lot, LotQRCode, LotReception
from apps.receptions.models import CoffeeReception, ReceptionStatus


class LotReceptionAssociationService:
    """Associate validated reception weight with a lot."""

    @classmethod
    @transaction.atomic
    def associate(
        cls,
        *,
        lot: Lot,
        reception: CoffeeReception,
        assigned_weight: Decimal,
        actor,
    ) -> LotReception:
        locked_lot = cls._lock_lot(lot)
        locked_reception = cls._lock_reception(reception)
        cls._validate_lot(locked_lot)
        cls._validate_reception(locked_reception)
        cls._validate_available_weight(
            lot=locked_lot,
            reception=locked_reception,
            assigned_weight=assigned_weight,
        )
        link = cls._save_link(
            lot=locked_lot,
            reception=locked_reception,
            assigned_weight=assigned_weight,
            actor=actor,
        )
        LotService.recalculate_total(locked_lot)
        return link

    @staticmethod
    def _lock_lot(lot: Lot) -> Lot:
        return Lot.objects.select_for_update().get(pk=lot.pk)

    @staticmethod
    def _lock_reception(reception: CoffeeReception) -> CoffeeReception:
        return CoffeeReception.objects.select_for_update().get(pk=reception.pk)

    @staticmethod
    def _validate_lot(lot: Lot) -> None:
        if not lot.is_active:
            raise ValidationError({"lot": "No se puede modificar un lote inactivo."})

    @staticmethod
    def _validate_reception(reception: CoffeeReception) -> None:
        if reception.status != ReceptionStatus.VALIDATED:
            raise ValidationError(
                {"reception": "Solo se pueden asociar recepciones con peso validado."}
            )

    @classmethod
    def _validate_available_weight(
        cls,
        *,
        lot: Lot,
        reception: CoffeeReception,
        assigned_weight: Decimal,
    ) -> None:
        available_weight = cls._available_weight(lot=lot, reception=reception)
        if assigned_weight <= available_weight:
            return
        raise ValidationError(
            {
                "assigned_weight_kg": (
                    f"El peso excede los {available_weight} kg disponibles de la recepción."
                )
            }
        )

    @staticmethod
    def _available_weight(*, lot: Lot, reception: CoffeeReception) -> Decimal:
        links = LotReception.objects.filter(reception=reception).exclude(lot=lot)
        used_weight = links.aggregate(total=Coalesce(Sum("assigned_weight_kg"), Decimal("0.00")))[
            "total"
        ]
        return reception.calculated_net_weight_kg - used_weight

    @staticmethod
    def _save_link(
        *,
        lot: Lot,
        reception: CoffeeReception,
        assigned_weight: Decimal,
        actor,
    ) -> LotReception:
        link, _ = LotReception.objects.update_or_create(
            lot=lot,
            reception=reception,
            defaults={"assigned_weight_kg": assigned_weight, "assigned_by": actor},
        )
        return link


class LotService:
    @staticmethod
    @transaction.atomic
    def create(*, actor, validated_data: dict) -> Lot:
        return Lot.objects.create(created_by=actor, **validated_data)

    @staticmethod
    @transaction.atomic
    def update(*, lot: Lot, validated_data: dict) -> Lot:
        for field, value in validated_data.items():
            setattr(lot, field, value)
        lot.save()
        return lot

    @staticmethod
    def associate_reception(
        *,
        lot: Lot,
        reception: CoffeeReception,
        assigned_weight: Decimal,
        actor,
    ) -> LotReception:
        return LotReceptionAssociationService.associate(
            lot=lot,
            reception=reception,
            assigned_weight=assigned_weight,
            actor=actor,
        )

    @staticmethod
    @transaction.atomic
    def remove_reception(*, link: LotReception) -> Lot:
        lot = link.lot
        link.delete()
        LotService.recalculate_total(lot)
        return lot

    @staticmethod
    def recalculate_total(lot: Lot) -> Lot:
        total = lot.reception_links.aggregate(
            value=Coalesce(Sum("assigned_weight_kg"), Decimal("0.00"))
        )["value"]
        lot.total_weight_kg = total
        lot.save(update_fields=["total_weight_kg", "updated_at"])
        return lot


class QRCodeService:
    @staticmethod
    @transaction.atomic
    def get_or_create(*, lot: Lot, actor) -> LotQRCode:
        qr_code, _ = LotQRCode.objects.get_or_create(
            lot=lot,
            defaults={"generated_by": actor},
        )
        if not qr_code.is_active:
            qr_code.is_active = True
            qr_code.generated_by = actor
            qr_code.save(update_fields=["is_active", "generated_by", "updated_at"])
        return qr_code
