from io import BytesIO

import qrcode
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.accounts.permissions import IsOperatorOrAdminOrReadOnly
from apps.audit.services import AuditService
from apps.common.viewsets import AuditedModelViewSet
from apps.lots.models import Lot, LotQRCode, LotReception
from apps.lots.serializers import (
    AssociateReceptionSerializer,
    LotQRCodeSerializer,
    LotReceptionSerializer,
    LotSerializer,
)
from apps.lots.services import LotService, QRCodeService


class LotViewSet(AuditedModelViewSet):
    serializer_class = LotSerializer
    permission_classes = [IsOperatorOrAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = [
        "code",
        "name",
        "reception_links__reception__producer__full_name",
        "reception_links__reception__code",
    ]
    ordering_fields = ["code", "name", "harvest_year", "total_weight_kg", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = (
            Lot.objects.select_related("created_by", "qr_code")
            .prefetch_related(
                "reception_links__reception__producer",
                "reception_links__reception__farm",
                "reception_links__assigned_by",
            )
            .annotate(
                producers_count=Count(
                    "reception_links__reception__producer",
                    distinct=True,
                )
            )
        )
        filters = {
            "status": self.request.query_params.get("status"),
            "harvest_year": self.request.query_params.get("harvest_year"),
        }
        return queryset.filter(**{key: value for key, value in filters.items() if value}).distinct()

    @action(detail=True, methods=["post"], url_path="associate-reception")
    def associate_reception(self, request, pk=None):
        lot = self.get_object()
        serializer = AssociateReceptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        link = LotService.associate_reception(
            lot=lot,
            reception=serializer.validated_data["reception"],
            assigned_weight=serializer.validated_data["assigned_weight_kg"],
            actor=request.user,
        )
        AuditService.record_action(
            request,
            lot,
            "ASSOCIATE_RECEPTION",
            {"reception_id": link.reception_id, "weight_kg": str(link.assigned_weight_kg)},
        )
        return Response(LotReceptionSerializer(link).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path=r"receptions/(?P<link_id>[^/.]+)/remove")
    def remove_reception(self, request, pk=None, link_id=None):
        lot = self.get_object()
        link = get_object_or_404(LotReception, pk=link_id, lot=lot)
        reception_id = link.reception_id
        LotService.remove_reception(link=link)
        AuditService.record_action(
            request,
            lot,
            "REMOVE_RECEPTION",
            {"reception_id": reception_id},
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="generate-qr")
    def generate_qr(self, request, pk=None):
        lot = self.get_object()
        qr_code = QRCodeService.get_or_create(lot=lot, actor=request.user)
        AuditService.record_action(request, lot, "GENERATE_QR", {"token": str(qr_code.token)})
        return Response(LotQRCodeSerializer(qr_code).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="qr-image")
    def qr_image(self, request, pk=None):
        lot = self.get_object()
        qr_code = get_object_or_404(LotQRCode, lot=lot, is_active=True)
        absolute_url = request.build_absolute_uri(f"/qr/{qr_code.token}/")
        image = qrcode.make(absolute_url)
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        response = HttpResponse(buffer.getvalue(), content_type="image/png")
        response["Content-Disposition"] = f'inline; filename="{lot.code}.png"'
        response["Cache-Control"] = "private, max-age=300"
        return response
