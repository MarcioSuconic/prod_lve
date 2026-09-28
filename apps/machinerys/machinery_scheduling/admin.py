from django.contrib import admin
from .models import MachineryScheduling


@admin.register(MachineryScheduling)
class MachinerySchedulingAdmin(admin.ModelAdmin):
    list_display = (
        "machinery",
        "datetime_initial",
        "datetime_finish",
        "register_production_sub_product",
        "active",
    )
    list_filter = ("machinery", "active")
    date_hierarchy = "datetime_initial"