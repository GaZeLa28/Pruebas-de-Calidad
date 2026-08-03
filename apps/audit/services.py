from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from django.forms.models import model_to_dict

from apps.audit.models import AuditLog


class AuditService:
    SENSITIVE_FIELDS = {
        "password",
        "token",
        "secret",
        "api_key",
        "access_token",
        "refresh_token",
    }

    @staticmethod
    def snapshot(instance) -> dict:
        values = model_to_dict(instance)
        return {
            key: AuditService._safe_field_value(key, value)
            for key, value in values.items()
        }

    @staticmethod
    def record_create(request, instance) -> AuditLog:
        return AuditService._record(
            request, instance, "CREATE", {}, AuditService.snapshot(instance)
        )

    @staticmethod
    def record_update(request, instance, before_data: dict) -> AuditLog:
        return AuditService._record(
            request, instance, "UPDATE", before_data, AuditService.snapshot(instance)
        )

    @staticmethod
    def record_action(request, instance, action: str, data: dict) -> AuditLog:
        return AuditService._record(request, instance, action, {}, data)

    @staticmethod
    def _record(request, instance, action: str, before_data: dict, after_data: dict) -> AuditLog:
        meta = instance._meta
        user = getattr(request, "user", None)
        return AuditLog.objects.create(
            actor=user if user and user.is_authenticated else None,
            action=action,
            app_label=meta.app_label,
            model_name=meta.model_name,
            object_id=str(instance.pk),
            object_repr=str(instance)[:255],
            before_data=AuditService._json_safe(before_data),
            after_data=AuditService._json_safe(after_data),
            ip_address=AuditService._client_ip(request),
        )

    @staticmethod
    def _safe_field_value(key: str, value):
        normalized_key = key.lower()
        if normalized_key in AuditService.SENSITIVE_FIELDS or normalized_key.endswith("_secret"):
            return "[REDACTED]"
        return AuditService._json_safe(value)

    @staticmethod
    def _client_ip(request) -> str | None:
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        return forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")

    @staticmethod
    def _json_safe(value):
        if isinstance(value, dict):
            return {
                key: AuditService._safe_field_value(str(key), item)
                for key, item in value.items()
            }
        if isinstance(value, (list, tuple, set)):
            return [AuditService._json_safe(item) for item in value]
        if isinstance(value, (datetime, date, Decimal, UUID)):
            return str(value)
        if hasattr(value, "pk"):
            return value.pk
        return value
