from rest_framework import serializers

from apps.lots.serializers import LotReceptionSerializer
from apps.traceability.models import TraceabilityEvent
from apps.traceability.services import TraceabilityService


class TraceabilityEventSerializer(serializers.ModelSerializer):
    lot_code = serializers.CharField(source="lot.code", read_only=True)
    reception_code = serializers.CharField(source="reception.code", read_only=True)
    event_type_display = serializers.CharField(source="get_event_type_display", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.get_full_name", read_only=True)

    class Meta:
        model = TraceabilityEvent
        fields = [
            "id",
            "lot",
            "lot_code",
            "reception",
            "reception_code",
            "event_type",
            "event_type_display",
            "occurred_at",
            "location",
            "description",
            "metadata",
            "recorded_by",
            "recorded_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "recorded_by", "created_at", "updated_at"]

    def validate(self, attrs):
        reception = attrs.get("reception", getattr(self.instance, "reception", None))
        lot = attrs.get("lot", getattr(self.instance, "lot", None))
        if reception and lot and not lot.reception_links.filter(reception=reception).exists():
            raise serializers.ValidationError(
                {"reception": "La recepción debe estar asociada al lote seleccionado."}
            )
        return attrs

    def create(self, validated_data):
        return TraceabilityService.create_event(
            actor=self.context["request"].user,
            validated_data=validated_data,
        )

    def update(self, instance, validated_data):
        return TraceabilityService.update_event(event=instance, validated_data=validated_data)


class TraceabilityTimelineSerializer(serializers.Serializer):
    lot = serializers.SerializerMethodField()
    origins = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()
    integrity = serializers.SerializerMethodField()

    def get_lot(self, obj) -> dict:
        qr_code = getattr(obj, "qr_code", None)
        return {
            "id": obj.id,
            "code": obj.code,
            "name": obj.name,
            "harvest_year": obj.harvest_year,
            "status": obj.status,
            "status_display": obj.get_status_display(),
            "total_weight_kg": str(obj.total_weight_kg),
            "qr_token": str(qr_code.token) if qr_code and qr_code.is_active else None,
        }

    def get_origins(self, obj) -> list[dict]:
        return LotReceptionSerializer(obj.reception_links.all(), many=True).data

    def get_events(self, obj) -> list[dict]:
        return TraceabilityEventSerializer(obj.traceability_events.all(), many=True).data

    def get_integrity(self, obj) -> dict:
        origins = list(obj.reception_links.all())
        return {
            "has_origins": bool(origins),
            "all_weights_validated": all(
                link.reception.status == "VALIDATED" for link in origins
            ),
            "has_events": obj.traceability_events.exists(),
            "origin_count": len(origins),
            "event_count": obj.traceability_events.count(),
        }
