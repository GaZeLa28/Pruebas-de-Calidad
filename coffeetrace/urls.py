from django.contrib import admin
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetCompleteView,
    PasswordResetConfirmView as DjangoPasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import include, path, reverse_lazy
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from apps.accounts.api_views import (
    CurrentUserView,
    LogoutTokenView,
    ObtainTokenView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    UserViewSet,
)
from apps.accounts.frontend_views import CoffeeTraceLoginView
from apps.audit.api_views import AuditLogViewSet
from apps.common.api_views import HealthCheckView
from apps.frontend.views import public_qr_page
from apps.lots.api_views import LotViewSet
from apps.producers.api_views import FarmViewSet, ProducerViewSet
from apps.receptions.api_views import CoffeeReceptionViewSet, WeightInconsistencyViewSet
from apps.traceability.api_views import LotTimelineView, PublicQRTraceabilityView, TraceabilityEventViewSet


router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("producers", ProducerViewSet, basename="producer")
router.register("farms", FarmViewSet, basename="farm")
router.register("receptions", CoffeeReceptionViewSet, basename="reception")
router.register("weight-inconsistencies", WeightInconsistencyViewSet, basename="weight-inconsistency")
router.register("lots", LotViewSet, basename="lot")
router.register("traceability-events", TraceabilityEventViewSet, basename="traceability-event")
router.register("audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", CoffeeTraceLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "password-reset/",
        PasswordResetView.as_view(
            template_name="registration/password_reset_form.html",
            email_template_name="registration/password_reset_email.txt",
            subject_template_name="registration/password_reset_subject.txt",
            success_url=reverse_lazy("password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        DjangoPasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("", include("apps.frontend.urls")),
    path("qr/<uuid:token>/", public_qr_page, name="public-qr"),
    path("api/v1/health/", HealthCheckView.as_view(), name="api-health"),
    path("api/v1/", include(router.urls)),
    path("api/v1/auth/login/", ObtainTokenView.as_view(), name="api-token-login"),
    path("api/v1/auth/logout/", LogoutTokenView.as_view(), name="api-token-logout"),
    path("api/v1/auth/me/", CurrentUserView.as_view(), name="api-current-user"),
    path(
        "api/v1/auth/password-reset/",
        PasswordResetRequestView.as_view(),
        name="api-password-reset",
    ),
    path(
        "api/v1/auth/password-reset-confirm/",
        PasswordResetConfirmView.as_view(),
        name="api-password-reset-confirm",
    ),
    path("api/v1/traceability/lots/<int:lot_id>/", LotTimelineView.as_view(), name="lot-timeline"),
    path("api/v1/traceability/qr/<uuid:token>/", PublicQRTraceabilityView.as_view(), name="public-qr-api"),
    path("api/v1/reports/", include("apps.reports.urls")),
    path(
        "api/schema/",
        get_schema_view(title="CoffeeTrace API", description="API REST de trazabilidad cafetalera", version="2.0.0"),
        name="openapi-schema",
    ),
    path("api-auth/", include("rest_framework.urls")),
]
