from django.contrib import admin
from .models import UtensilScheduling


@admin.register(UtensilScheduling)
class MachinerySchedulingAdmin(admin.ModelAdmin):
    list_display = (
        "utensil",
        "datetime_initial",
        "datetime_finish",
        "register_production_sub_product",
        "active",
    )
    list_filter = ("utensil", "active")
    date_hierarchy = "datetime_initial"