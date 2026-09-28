from django.contrib import admin
from .models import SubProduct


@admin.register(SubProduct)
class SubProductAdmin(admin.ModelAdmin):
    list_display = ("sub_product", "base_recipe", "sub_product_sub_type", "active")
    list_filter = ("sub_product_sub_type", "active")
    search_fields = ("sub_product",)
    autocomplete_fields = ("base_recipe",)
