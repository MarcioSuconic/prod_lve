from django.contrib import admin
from .models import PhysicalQuantity


@admin.register(PhysicalQuantity)
class PhysicalQuantityAdmin(admin.ModelAdmin):
    list_display = ("physical_quantity",)
    search_fields = ("physical_quantity",)