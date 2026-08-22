from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.accounts.models import UserRole


def get_role(user) -> str:
    if not user or not user.is_authenticated:
        return ""
    if user.is_superuser:
        return UserRole.ADMIN
    profile = getattr(user, "profile", None)
    return getattr(profile, "role", UserRole.VIEWER)


class IsAdmin(BasePermission):
    message = "Se requiere el rol Administrador."

    def has_permission(self, request, view) -> bool:
        return get_role(request.user) == UserRole.ADMIN


class IsOperatorOrAdminOrReadOnly(BasePermission):
    message = "Se requiere el rol Operador o Administrador."

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return get_role(request.user) in {UserRole.ADMIN, UserRole.OPERATOR}


class IsAuditorOrAdmin(BasePermission):
    message = "Se requiere el rol Auditor o Administrador."

    def has_permission(self, request, view) -> bool:
        return get_role(request.user) in {UserRole.ADMIN, UserRole.AUDITOR}
