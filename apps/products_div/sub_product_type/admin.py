from django.contrib import admin
from .models import SubProductType


@admin.register(SubProductType)
class SubProductTypeAdmin(admin.ModelAdmin):
    list_display = ("sub_product_type", "active")
    list_filter = ("active",)
    search_fields = ("sub_product_type",)
