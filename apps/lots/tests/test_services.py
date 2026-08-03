from decimal import Decimal

import pytest
from rest_framework.exceptions import ValidationError

from apps.common.tests.factories import create_origin, create_user
from apps.lots.models import Lot
from apps.lots.services import LotService
from apps.receptions.models import ReceptionStatus


@pytest.mark.django_db
class TestLotService:
    def test_associates_validated_reception_and_recalculates_weight(self):
        actor = create_user()
        _, _, reception = create_origin(actor=actor)
        lot = LotService.create(
            actor=actor,
            validated_data={"code": "L-001", "name": "Lote prueba", "harvest_year": 2026},
        )
        LotService.associate_reception(
            lot=lot,
            reception=reception,
            assigned_weight=Decimal("75.00"),
            actor=actor,
        )
        lot.refresh_from_db()
        assert lot.total_weight_kg == Decimal("75.00")

    def test_rejects_weight_greater_than_available(self):
        actor = create_user()
        _, _, reception = create_origin(actor=actor)
        lot = Lot.objects.create(code="L-002", name="Lote prueba", harvest_year=2026, created_by=actor)
        with pytest.raises(ValidationError):
            LotService.associate_reception(
                lot=lot,
                reception=reception,
                assigned_weight=Decimal("101.00"),
                actor=actor,
            )

    def test_rejects_reception_that_is_not_validated(self):
        actor = create_user()
        _, _, reception = create_origin(actor=actor)
        reception.status = ReceptionStatus.PENDING
        reception.save(update_fields=["status"])
        lot = Lot.objects.create(
            code="L-003",
            name="Lote pendiente",
            harvest_year=2026,
            created_by=actor,
        )
        with pytest.raises(ValidationError):
            LotService.associate_reception(
                lot=lot,
                reception=reception,
                assigned_weight=Decimal("50.00"),
                actor=actor,
            )
