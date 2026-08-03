from django.contrib import admin

from apps.traceability.models import TraceabilityEvent


@admin.register(TraceabilityEvent)
class TraceabilityEventAdmin(admin.ModelAdmin):
    list_display = ("lot", "event_type", "occurred_at", "location", "recorded_by")
    list_filter = ("event_type", "occurred_at")
    search_fields = ("lot__code", "description", "location")
    autocomplete_fields = ("lot", "reception", "recorded_by")
