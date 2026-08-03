import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import UserRole
from apps.common.tests.factories import create_user


@pytest.mark.django_db
class TestProducerAPI:
    def test_admin_can_create_producer(self):
        client = APIClient()
        client.force_authenticate(create_user())
        response = client.post(
            reverse("producer-list"),
            {
                "code": "P-100",
                "national_id": "1-2222-3333",
                "full_name": "Elena Mora",
                "phone": "8888-0000",
                "is_active": True,
            },
            format="json",
        )
        assert response.status_code == 201
        assert response.data["created_by"] is not None

    def test_viewer_cannot_create_producer(self):
        client = APIClient()
        client.force_authenticate(create_user(username="viewer", role=UserRole.VIEWER))
        response = client.post(
            reverse("producer-list"),
            {"code": "P-101", "national_id": "1-9999-9999", "full_name": "Sin permiso"},
            format="json",
        )
        assert response.status_code == 403
