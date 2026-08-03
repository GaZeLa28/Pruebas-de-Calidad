from django.contrib import admin
from apps.audit.models import AuditLog
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "actor", "action", "model_name", "object_repr")
    list_filter = ("action", "app_label", "model_name")
    search_fields = ("object_repr", "object_id", "actor__username")
    readonly_fields = [field.name for field in AuditLog._meta.fields]
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
