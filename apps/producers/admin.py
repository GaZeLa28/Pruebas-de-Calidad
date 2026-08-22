from django.contrib import admin

from apps.producers.models import Farm, Producer


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    list_display = ("code", "full_name", "national_id", "phone", "is_active")
    search_fields = ("code", "full_name", "national_id")
    list_filter = ("is_active",)


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "producer", "province", "canton", "is_active")
    search_fields = ("code", "name", "producer__full_name")
    list_filter = ("province", "is_active")
    autocomplete_fields = ("producer",)
