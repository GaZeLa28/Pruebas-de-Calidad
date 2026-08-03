from django.contrib import admin

from apps.receptions.models import CoffeeReception, WeightInconsistency


@admin.register(CoffeeReception)
class CoffeeReceptionAdmin(admin.ModelAdmin):
    list_display = ("code", "producer", "farm", "received_at", "calculated_net_weight_kg", "status")
    list_filter = ("status", "coffee_variety", "received_at")
    search_fields = ("code", "producer__full_name", "farm__name")
    autocomplete_fields = ("producer", "farm", "received_by")


@admin.register(WeightInconsistency)
class WeightInconsistencyAdmin(admin.ModelAdmin):
    list_display = ("reception", "difference_kg", "status", "created_at", "resolved_at")
    list_filter = ("status",)
    search_fields = ("reception__code", "reception__producer__full_name")
