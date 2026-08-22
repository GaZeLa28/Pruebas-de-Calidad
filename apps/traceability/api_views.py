from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny

from apps.accounts.permissions import IsOperatorOrAdminOrReadOnly
from apps.common.viewsets import AuditedModelViewSet
from apps.traceability.models import TraceabilityEvent
from apps.traceability.selectors import TraceabilitySelector
from apps.traceability.serializers import (
    TraceabilityEventSerializer,
    TraceabilityTimelineSerializer,
)


class TraceabilityEventViewSet(AuditedModelViewSet):
    serializer_class = TraceabilityEventSerializer
    permission_classes = [IsOperatorOrAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["lot__code", "reception__code", "description", "location"]
    ordering_fields = ["occurred_at", "event_type", "created_at"]
    ordering = ["occurred_at"]

    def get_queryset(self):
        queryset = TraceabilityEvent.objects.select_related("lot", "reception", "recorded_by")
        filters = {
            "lot_id": self.request.query_params.get("lot"),
            "event_type": self.request.query_params.get("event_type"),
        }
        return queryset.filter(**{key: value for key, value in filters.items() if value})


class LotTimelineView(RetrieveAPIView):
    serializer_class = TraceabilityTimelineSerializer
    lookup_url_kwarg = "lot_id"
    lookup_field = "id"

    def get_queryset(self):
        return TraceabilitySelector.lot_timeline_queryset()


class PublicQRTraceabilityView(RetrieveAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = TraceabilityTimelineSerializer
    lookup_url_kwarg = "token"
    lookup_field = "qr_code__token"

    def get_queryset(self):
        return TraceabilitySelector.lot_timeline_queryset().filter(qr_code__is_active=True)
