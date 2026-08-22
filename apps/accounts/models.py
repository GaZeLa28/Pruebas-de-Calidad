from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class UserRole(models.TextChoices):
    ADMIN = "ADMIN", "Administrador"
    OPERATOR = "OPERATOR", "Operador"
    AUDITOR = "AUDITOR", "Auditor"
    VIEWER = "VIEWER", "Consulta"


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.VIEWER)
    phone = models.CharField(max_length=30, blank=True)

    class Meta:
        verbose_name = "perfil de usuario"
        verbose_name_plural = "perfiles de usuario"

    def __str__(self) -> str:
        return f"{self.user.username} - {self.get_role_display()}"
