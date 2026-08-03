from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError

from apps.accounts.models import UserProfile, UserRole

User = get_user_model()


class UserService:
    @staticmethod
    @transaction.atomic
    def create_user(*, password: str, role: str = UserRole.VIEWER, **validated_data):
        user = User.objects.create_user(password=password, **validated_data)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.save(update_fields=["role", "updated_at"])
        return user

    @staticmethod
    @transaction.atomic
    def update_user(*, user, password: str | None = None, role: str | None = None, **data):
        for field, value in data.items():
            setattr(user, field, value)
        if password:
            user.set_password(password)
        user.save()
        if role is not None:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.save(update_fields=["role", "updated_at"])
        return user


class PasswordResetService:
    @staticmethod
    def request_reset(*, request, email: str) -> None:
        users = User.objects.filter(email__iexact=email, is_active=True).only(
            "id", "username", "email"
        )
        for user in users:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            path = reverse(
                "password_reset_confirm",
                kwargs={"uidb64": uid, "token": token},
            )
            reset_url = request.build_absolute_uri(path)
            send_mail(
                subject="Restablecimiento de contraseña de CoffeeTrace",
                message=(
                    f"Hola {user.get_username()},\n\n"
                    "Se solicitó restablecer su contraseña de CoffeeTrace. "
                    f"Abra este enlace para continuar:\n{reset_url}\n\n"
                    "Ignore este mensaje si no realizó la solicitud."
                ),
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False,
            )

    @staticmethod
    @transaction.atomic
    def confirm_reset(*, uid: str, token: str, new_password: str):
        user = PasswordResetService._resolve_user(uid)
        if user is None or not default_token_generator.check_token(user, token):
            raise ValidationError({"token": "El enlace es inválido o ya expiró."})
        try:
            validate_password(new_password, user=user)
        except DjangoValidationError as error:
            raise ValidationError({"new_password": list(error.messages)}) from error
        user.set_password(new_password)
        user.save(update_fields=["password"])
        Token.objects.filter(user=user).delete()
        return user

    @staticmethod
    def _resolve_user(uid: str):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            return User.objects.get(pk=user_id, is_active=True)
        except TypeError, ValueError, OverflowError, User.DoesNotExist:
            return None
