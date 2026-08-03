from django.urls import path

from apps.frontend import views


urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("manage/<slug:resource>/", views.resource_page, name="resource-page"),
    path("lots/<int:lot_id>/", views.lot_detail, name="lot-detail"),
    path("reports/", views.reports_page, name="reports-page"),
]
