from django.contrib import admin

from apps.machinerys.machinery.models import Machinery


@admin.register(Machinery)
class MachineryAdmin(admin.ModelAdmin):
    list_display = ("code", "machinery", "store", "qtde_power", "unit_power", "active")
    list_filter = ("store", "active")
    search_fields = ("machinery", "code")


