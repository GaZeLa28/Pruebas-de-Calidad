from __future__ import annotations

from django.db import transaction

from apps.traceability.models import TraceabilityEvent


class TraceabilityService:
    @staticmethod
    @transaction.atomic
    def create_event(*, actor, validated_data: dict) -> TraceabilityEvent:
        return TraceabilityEvent.objects.create(recorded_by=actor, **validated_data)

    @staticmethod
    @transaction.atomic
    def update_event(*, event: TraceabilityEvent, validated_data: dict) -> TraceabilityEvent:
        for field, value in validated_data.items():
            setattr(event, field, value)
        event.save()
        return event
