from rest_framework import viewsets

from apps.accounts.permissions import IsAuditorOrAdmin
from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuditorOrAdmin]

    def get_queryset(self):
        queryset = AuditLog.objects.select_related("actor")
        if model_name := self.request.query_params.get("model"):
            queryset = queryset.filter(model_name=model_name)
        if action := self.request.query_params.get("action"):
            queryset = queryset.filter(action=action)
        return queryset
