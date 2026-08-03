from decimal import Decimal

from rest_framework import serializers

from apps.lots.models import Lot, LotQRCode, LotReception
from apps.lots.services import LotService
from apps.receptions.models import CoffeeReception


class LotReceptionSerializer(serializers.ModelSerializer):
    reception_code = serializers.CharField(source="reception.code", read_only=True)
    producer_name = serializers.CharField(source="reception.producer.full_name", read_only=True)
    farm_name = serializers.CharField(source="reception.farm.name", read_only=True)
    assigned_by_name = serializers.CharField(source="assigned_by.get_full_name", read_only=True)

    class Meta:
        model = LotReception
        fields = [
            "id",
            "reception",
            "reception_code",
            "producer_name",
            "farm_name",
            "assigned_weight_kg",
            "assigned_by",
            "assigned_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "assigned_by", "created_at", "updated_at"]


class LotQRCodeSerializer(serializers.ModelSerializer):
    public_path = serializers.SerializerMethodField()
    image_path = serializers.SerializerMethodField()

    class Meta:
        model = LotQRCode
        fields = ["id", "token", "is_active", "public_path", "image_path", "created_at"]
        read_only_fields = fields

    def get_public_path(self, obj) -> str:
        return f"/qr/{obj.token}/"

    def get_image_path(self, obj) -> str:
        return f"/api/v1/lots/{obj.lot_id}/qr-image/"


class LotSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    reception_links = LotReceptionSerializer(many=True, read_only=True)
    qr_code = LotQRCodeSerializer(read_only=True)
    producers_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Lot
        fields = [
            "id",
            "code",
            "name",
            "harvest_year",
            "warehouse_location",
            "status",
            "status_display",
            "total_weight_kg",
            "notes",
            "is_active",
            "created_by",
            "created_by_name",
            "reception_links",
            "qr_code",
            "producers_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "total_weight_kg",
            "created_by",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        return LotService.create(actor=self.context["request"].user, validated_data=validated_data)

    def update(self, instance, validated_data):
        return LotService.update(lot=instance, validated_data=validated_data)


class AssociateReceptionSerializer(serializers.Serializer):
    reception_id = serializers.PrimaryKeyRelatedField(
        queryset=CoffeeReception.objects.select_related("producer", "farm"),
        source="reception",
    )
    assigned_weight_kg = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )
