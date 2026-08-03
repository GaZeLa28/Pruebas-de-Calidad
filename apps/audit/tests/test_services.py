import pytest
from django.test import RequestFactory

from apps.audit.services import AuditService
from apps.common.tests.factories import create_user


@pytest.mark.django_db
class TestAuditService:
    def test_redacts_password_hash_from_user_snapshot(self):
        user = create_user()
        snapshot = AuditService.snapshot(user)
        assert snapshot["password"] == "[REDACTED]"

    def test_records_authenticated_actor(self):
        user = create_user()
        request = RequestFactory().post("/api/v1/users/")
        request.user = user
        log = AuditService.record_action(request, user, "SECURITY_TEST", {"token": "secret"})
        assert log.actor == user
        assert log.after_data["token"] == "[REDACTED]"
