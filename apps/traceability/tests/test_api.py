from decimal import Decimal

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.common.tests.factories import create_origin, create_user
from apps.lots.services import LotService, QRCodeService


@pytest.mark.django_db
class TestPublicTraceabilityAPI:
    def test_qr_endpoint_is_public(self):
        actor = create_user()
        _, _, reception = create_origin(actor=actor)
        lot = LotService.create(
            actor=actor,
            validated_data={"code": "L-QR", "name": "Lote QR", "harvest_year": 2026},
        )
        LotService.associate_reception(
            lot=lot,
            reception=reception,
            assigned_weight=Decimal("100.00"),
            actor=actor,
        )
        qr_code = QRCodeService.get_or_create(lot=lot, actor=actor)
        response = APIClient().get(reverse("public-qr-api", kwargs={"token": qr_code.token}))
        assert response.status_code == 200
        assert response.data["lot"]["code"] == "L-QR"
