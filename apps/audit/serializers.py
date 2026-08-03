from rest_framework import serializers
from apps.audit.models import AuditLog
from apps.common.serializers import ActorSerializer
class AuditLogSerializer(serializers.ModelSerializer):
    actor = ActorSerializer(read_only=True)
    class Meta:
        model = AuditLog
        fields = ["id", "actor", "action", "app_label", "model_name", "object_id", "object_repr", "before_data", "after_data", "ip_address", "created_at"]
