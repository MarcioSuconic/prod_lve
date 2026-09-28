from django.contrib import admin
from .models import ElectricPower_x_Store


@admin.register(ElectricPower_x_Store)
class ElectricPowerXStoreAdmin(admin.ModelAdmin):
    list_display = ("store", "fare_amount_kwh", "date")
    list_filter = ("store", "date")
    date_hierarchy = "date"