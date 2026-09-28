from django.contrib import admin
from .models import SubProductSubType


@admin.register(SubProductSubType)
class SubProductSubTypeAdmin(admin.ModelAdmin):
    list_display = ("sub_product_sub_type", "type", "active")
    list_filter = ("type", "active")
    search_fields = ("sub_product_sub_type",)