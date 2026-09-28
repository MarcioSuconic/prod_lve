from django.contrib import admin
from .models import Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name_store", "id_store", "active")
    list_filter = ("active",)
    search_fields = ("name_store", "id_store")
