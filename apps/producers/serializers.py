from rest_framework import serializers

from apps.producers.models import Farm, Producer


class ProducerSerializer(serializers.ModelSerializer):
    farms_count = serializers.IntegerField(read_only=True, default=0)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = Producer
        fields = [
            "id",
            "code",
            "national_id",
            "full_name",
            "email",
            "phone",
            "address",
            "is_active",
            "farms_count",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]


class FarmSerializer(serializers.ModelSerializer):
    producer_name = serializers.CharField(source="producer.full_name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = Farm
        fields = [
            "id",
            "producer",
            "producer_name",
            "code",
            "name",
            "province",
            "canton",
            "district",
            "address",
            "latitude",
            "longitude",
            "altitude_masl",
            "area_hectares",
            "certification",
            "is_active",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]
