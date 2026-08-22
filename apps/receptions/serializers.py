from rest_framework import serializers

from apps.receptions.models import CoffeeReception, WeightInconsistency
from apps.receptions.services import InconsistencyService, ReceptionService


class CoffeeReceptionSerializer(serializers.ModelSerializer):
    producer_name = serializers.CharField(source="producer.full_name", read_only=True)
    farm_name = serializers.CharField(source="farm.name", read_only=True)
    received_by_name = serializers.CharField(source="received_by.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    open_inconsistencies = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = CoffeeReception
        fields = [
            "id",
            "code",
            "producer",
            "producer_name",
            "farm",
            "farm_name",
            "received_by",
            "received_by_name",
            "received_at",
            "coffee_variety",
            "process_type",
            "gross_weight_kg",
            "tare_weight_kg",
            "declared_net_weight_kg",
            "calculated_net_weight_kg",
            "moisture_percentage",
            "status",
            "status_display",
            "notes",
            "open_inconsistencies",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "received_by",
            "calculated_net_weight_kg",
            "status",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        return ReceptionService.create(
            actor=self.context["request"].user, validated_data=validated_data
        )

    def update(self, instance, validated_data):
        return ReceptionService.update(reception=instance, validated_data=validated_data)


class WeightInconsistencySerializer(serializers.ModelSerializer):
    reception_code = serializers.CharField(source="reception.code", read_only=True)
    producer_name = serializers.CharField(source="reception.producer.full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    resolved_by_name = serializers.CharField(source="resolved_by.get_full_name", read_only=True)

    class Meta:
        model = WeightInconsistency
        fields = [
            "id",
            "reception",
            "reception_code",
            "producer_name",
            "difference_kg",
            "description",
            "status",
            "status_display",
            "resolved_by",
            "resolved_by_name",
            "resolution_notes",
            "resolved_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class ResolveInconsistencySerializer(serializers.Serializer):
    resolution_notes = serializers.CharField(min_length=5, max_length=1000)

    def save(self, **kwargs):
        return InconsistencyService.resolve(
            inconsistency=self.context["inconsistency"],
            actor=self.context["request"].user,
            notes=self.validated_data["resolution_notes"],
        )
