from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import UserProfile
from apps.audit.services import AuditService

User = get_user_model()


@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance, created, **kwargs) -> None:
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(user_logged_in)
def audit_web_login(sender, request, user, **kwargs) -> None:
    AuditService.record_action(request, user, "WEB_LOGIN", {"username": user.username})


@receiver(user_logged_out)
def audit_web_logout(sender, request, user, **kwargs) -> None:
    if user is not None:
        AuditService.record_action(request, user, "WEB_LOGOUT", {"username": user.username})
