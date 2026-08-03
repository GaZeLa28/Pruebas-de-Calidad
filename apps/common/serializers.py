from rest_framework import serializers
class ActorSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    full_name = serializers.SerializerMethodField()
    def get_full_name(self, obj) -> str:
        return obj.get_full_name() or obj.username
