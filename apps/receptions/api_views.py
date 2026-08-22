from django.db.models import Count, Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.accounts.permissions import IsOperatorOrAdminOrReadOnly
from apps.audit.services import AuditService
from apps.common.viewsets import AuditedModelViewSet
from apps.receptions.models import CoffeeReception, WeightInconsistency
from apps.receptions.serializers import (
    CoffeeReceptionSerializer,
    ResolveInconsistencySerializer,
    WeightInconsistencySerializer,
)


class CoffeeReceptionViewSet(AuditedModelViewSet):
    serializer_class = CoffeeReceptionSerializer
    permission_classes = [IsOperatorOrAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["code", "producer__full_name", "farm__name", "coffee_variety"]
    ordering_fields = ["received_at", "code", "calculated_net_weight_kg", "created_at"]
    ordering = ["-received_at"]

    def get_queryset(self):
        queryset = CoffeeReception.objects.select_related(
            "producer", "farm", "received_by"
        ).annotate(
            open_inconsistencies=Count(
                "weight_inconsistencies",
                filter=Q(weight_inconsistencies__status="OPEN"),
            )
        )
        filters = {
            "producer_id": self.request.query_params.get("producer"),
            "farm_id": self.request.query_params.get("farm"),
            "status": self.request.query_params.get("status"),
        }
        return queryset.filter(**{key: value for key, value in filters.items() if value})


class WeightInconsistencyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WeightInconsistencySerializer
    permission_classes = [IsOperatorOrAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["reception__code", "reception__producer__full_name", "description"]
    ordering_fields = ["created_at", "difference_kg", "resolved_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = WeightInconsistency.objects.select_related(
            "reception", "reception__producer", "resolved_by"
        )
        item_status = self.request.query_params.get("status")
        return queryset.filter(status=item_status) if item_status else queryset

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        inconsistency = self.get_object()
        serializer = ResolveInconsistencySerializer(
            data=request.data,
            context={"request": request, "inconsistency": inconsistency},
        )
        serializer.is_valid(raise_exception=True)
        resolved = serializer.save()
        AuditService.record_action(request, resolved, "RESOLVE", {"status": resolved.status})
        return Response(WeightInconsistencySerializer(resolved).data, status=status.HTTP_200_OK)
