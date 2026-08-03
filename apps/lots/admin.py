from django.contrib import admin

from apps.lots.models import Lot, LotQRCode, LotReception


class LotReceptionInline(admin.TabularInline):
    model = LotReception
    extra = 0
    autocomplete_fields = ("reception", "assigned_by")


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "harvest_year", "status", "total_weight_kg", "is_active")
    search_fields = ("code", "name")
    list_filter = ("harvest_year", "status", "is_active")
    inlines = (LotReceptionInline,)


@admin.register(LotQRCode)
class LotQRCodeAdmin(admin.ModelAdmin):
    list_display = ("lot", "token", "is_active", "created_at")
    search_fields = ("lot__code", "token")
    list_filter = ("is_active",)
