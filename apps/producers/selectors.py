from django.db.models import QuerySet

from apps.producers.models import Farm, Producer


class ProducerSelector:
    @staticmethod
    def list_with_farms() -> QuerySet[Producer]:
        return Producer.objects.select_related("created_by").prefetch_related("farms")


class FarmSelector:
    @staticmethod
    def list_detailed() -> QuerySet[Farm]:
        return Farm.objects.select_related("producer", "created_by")
