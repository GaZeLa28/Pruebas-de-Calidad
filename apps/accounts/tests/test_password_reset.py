import pytest
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.exceptions import ValidationError

from apps.accounts.services import PasswordResetService
from apps.common.tests.factories import create_user


@pytest.mark.django_db
class TestPasswordResetService:
    def test_sends_reset_message_for_active_user(self, rf, settings):
        settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
        user = create_user()
        request = rf.post("/api/v1/auth/password-reset/", HTTP_HOST="testserver")
        PasswordResetService.request_reset(request=request, email=user.email)
        assert len(mail.outbox) == 1
        assert "password-reset" in mail.outbox[0].body

    def test_changes_password_and_invalidates_token(self):
        user = create_user()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        PasswordResetService.confirm_reset(
            uid=uid,
            token=token,
            new_password="NuevaClaveSegura2026!",
        )
        user.refresh_from_db()
        assert user.check_password("NuevaClaveSegura2026!")

    def test_rejects_invalid_token(self):
        user = create_user()
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        with pytest.raises(ValidationError):
            PasswordResetService.confirm_reset(
                uid=uid,
                token="invalid-token",
                new_password="NuevaClaveSegura2026!",
            )
