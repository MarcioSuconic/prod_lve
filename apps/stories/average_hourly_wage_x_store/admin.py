from django.contrib import admin
from .models import AverageHourlyWage_x_Store


@admin.register(AverageHourlyWage_x_Store)
class AverageHourlyWageXStoreAdmin(admin.ModelAdmin):
    list_display = ("store", "average_hourly_wage", "date")
    list_filter = ("store", "date")
    date_hierarchy = "date"
