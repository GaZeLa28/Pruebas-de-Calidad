from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from apps.accounts.models import UserRole
from apps.accounts.permissions import get_role
from apps.accounts.services import PasswordResetService, UserService
User = get_user_model()
class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=UserRole.choices, write_only=True, required=False)
    role_code = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False, min_length=10)
    full_name = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "full_name", "email", "is_active", "role", "role_code", "role_display", "password", "date_joined"]
        read_only_fields = ["id", "date_joined"]
    def get_full_name(self, obj) -> str:
        return obj.get_full_name() or obj.username
    def get_role_code(self, obj) -> str:
        return get_role(obj)

    def get_role_display(self, obj) -> str:
        return UserRole(get_role(obj)).label
    def validate(self, attrs):
        if self.instance is None and not attrs.get("password"):
            raise serializers.ValidationError({"password": "La contraseña es obligatoria."})
        return attrs
    def create(self, validated_data):
        role = validated_data.pop("role", UserRole.VIEWER)
        password = validated_data.pop("password")
        return UserService.create_user(password=password, role=role, **validated_data)
    def update(self, instance, validated_data):
        role = validated_data.pop("role", None)
        password = validated_data.pop("password", None)
        return UserService.update_user(user=instance, password=password, role=role, **validated_data)
class TokenLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    def validate(self, attrs):
        user = authenticate(request=self.context.get("request"), username=attrs["username"], password=attrs["password"])
        if user is None or not user.is_active:
            raise serializers.ValidationError("Credenciales inválidas o usuario inactivo.")
        attrs["user"] = user
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def save(self, **kwargs):
        PasswordResetService.request_reset(
            request=self.context["request"],
            email=self.validated_data["email"],
        )


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=10)

    def save(self, **kwargs):
        return PasswordResetService.confirm_reset(
            uid=self.validated_data["uid"],
            token=self.validated_data["token"],
            new_password=self.validated_data["new_password"],
        )
