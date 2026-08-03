from django.db import DatabaseError
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.database_health import DatabaseHealthService


class HealthCheckView(APIView):
    """Return application availability without exposing connection credentials."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):
        try:
            DatabaseHealthService.inspect()
        except (DatabaseError, RuntimeError):
            return Response(
                {"status": "unavailable", "database": "disconnected"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({"status": "ok", "database": "connected"})
