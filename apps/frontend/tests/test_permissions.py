import pytest
from django.urls import reverse

from apps.accounts.models import UserRole
from apps.common.tests.factories import create_user


@pytest.mark.django_db
class TestFrontendPermissions:
    def test_viewer_cannot_open_reports(self, client):
        client.force_login(create_user(role=UserRole.VIEWER))
        response = client.get(reverse("reports-page"))
        assert response.status_code == 403

    def test_auditor_can_open_reports(self, client):
        client.force_login(create_user(username="auditor", role=UserRole.AUDITOR))
        response = client.get(reverse("reports-page"))
        assert response.status_code == 200
