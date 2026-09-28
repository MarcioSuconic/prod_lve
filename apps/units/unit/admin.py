from django.contrib import admin
from .models import Unit


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ("unit", "symbol", "physical_quantity", "is_benchmark")
    list_filter = ("physical_quantity", "is_benchmark")
    search_fields = ("unit", "symbol")