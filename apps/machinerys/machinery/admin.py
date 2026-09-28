from django.contrib import admin
from .models import Machinery


@admin.register(Machinery)
class MachineryAdmin(admin.ModelAdmin):
    list_display = ("machinery", "store", "qtde_power", "unit_power", "active")
    list_filter = ("store", "active")
    search_fields = ("machinery",)
