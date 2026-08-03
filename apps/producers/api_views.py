from django.db.models import Count, Q
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.accounts.permissions import IsOperatorOrAdminOrReadOnly
from apps.common.viewsets import AuditedModelViewSet
from apps.producers.models import Farm, Producer
from apps.producers.serializers import FarmSerializer, ProducerSerializer


class ProducerViewSet(AuditedModelViewSet):
    serializer_class = ProducerSerializer
    permission_classes = [IsOperatorOrAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["code", "national_id", "full_name", "email", "phone"]
    ordering_fields = ["code", "full_name", "created_at", "updated_at"]
    ordering = ["full_name"]

    def get_queryset(self):
        queryset = Producer.objects.select_related("created_by").annotate(
            farms_count=Count("farms", filter=Q(farms__is_active=True))
        )
        active = self.request.query_params.get("is_active")
        return queryset.filter(is_active=active.lower() == "true") if active else queryset

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        self.audit_service_class.record_create(self.request, instance)


class FarmViewSet(AuditedModelViewSet):
    serializer_class = FarmSerializer
    permission_classes = [IsOperatorOrAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["code", "name", "producer__full_name", "province", "canton", "district"]
    ordering_fields = ["code", "name", "created_at", "updated_at"]
    ordering = ["producer__full_name", "name"]

    def get_queryset(self):
        queryset = Farm.objects.select_related("producer", "created_by")
        producer_id = self.request.query_params.get("producer")
        active = self.request.query_params.get("is_active")
        if producer_id:
            queryset = queryset.filter(producer_id=producer_id)
        if active:
            queryset = queryset.filter(is_active=active.lower() == "true")
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        self.audit_service_class.record_create(self.request, instance)
