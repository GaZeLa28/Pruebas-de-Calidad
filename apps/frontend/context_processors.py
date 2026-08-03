from apps.accounts.models import UserRole
from apps.accounts.permissions import get_role


def user_profile(request) -> dict:
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {
            "current_role": "",
            "current_role_display": "",
            "can_write_operational_data": False,
        }

    role = get_role(user)
    profile = getattr(user, "profile", None)
    role_display = (
        UserRole(role).label if user.is_superuser or profile is None else profile.get_role_display()
    )
    return {
        "current_role": role,
        "current_role_display": role_display,
        "can_write_operational_data": role in {UserRole.ADMIN, UserRole.OPERATOR},
    }
