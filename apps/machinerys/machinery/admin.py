from django.contrib import admin

from .models import Machinery, Utensil


@admin.register(Machinery)
class MachineryAdmin(admin.ModelAdmin):
    list_display = ("code", "machinery", "store", "qtde_power", "unit_power", "active")
    list_filter = ("store", "active")
    search_fields = ("machinery", "code")


@admin.register(Utensil)
class UtensilAdmin(admin.ModelAdmin):
    list_display = ("code", "utensil", "store", "active")
    list_filter = ("store", "active")
    search_fields = ("utensil", "code")
