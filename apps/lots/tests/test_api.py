import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.common.tests.factories import create_user
from apps.lots.services import LotService


@pytest.mark.django_db
class TestLotQRCodeAPI:
    def test_qr_image_read_does_not_create_qr(self):
        actor = create_user()
        lot = LotService.create(
            actor=actor,
            validated_data={"code": "L-NO-QR", "name": "Sin QR", "harvest_year": 2026},
        )
        client = APIClient()
        client.force_authenticate(actor)
        response = client.get(reverse("lot-qr-image", kwargs={"pk": lot.pk}))
        assert response.status_code == 404
        assert not hasattr(lot, "qr_code")
