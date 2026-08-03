from django.db.models import Prefetch, QuerySet

from apps.lots.models import Lot, LotReception
from apps.traceability.models import TraceabilityEvent


class TraceabilitySelector:
    @staticmethod
    def lot_timeline_queryset() -> QuerySet[Lot]:
        links = LotReception.objects.select_related(
            "reception__producer",
            "reception__farm",
        )
        events = TraceabilityEvent.objects.select_related("recorded_by", "reception")
        return Lot.objects.select_related("qr_code").prefetch_related(
            Prefetch("reception_links", queryset=links),
            Prefetch("traceability_events", queryset=events),
        )
