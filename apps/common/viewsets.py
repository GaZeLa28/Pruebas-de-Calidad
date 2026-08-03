from rest_framework import viewsets
from apps.audit.services import AuditService
class AuditedModelViewSet(viewsets.ModelViewSet):
    """Base CRUD auditable. No permite eliminación destructiva."""
    http_method_names = ["get", "post", "put", "patch", "head", "options"]
    audit_service_class = AuditService
    def perform_create(self, serializer):
        instance = serializer.save()
        self.audit_service_class.record_create(self.request, instance)
    def perform_update(self, serializer):
        before = self.audit_service_class.snapshot(serializer.instance)
        instance = serializer.save()
        self.audit_service_class.record_update(self.request, instance, before)
