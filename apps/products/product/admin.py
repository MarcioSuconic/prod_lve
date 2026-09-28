from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("product", "store", "sub_category", "active")
    list_filter = ("store", "sub_category", "active")
    search_fields = ("product", "name_menu")
