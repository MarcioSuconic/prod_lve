from django.contrib import admin
from .models import Product_x_Sub_Product


@admin.register(Product_x_Sub_Product)
class ProductXSubProductAdmin(admin.ModelAdmin):
    list_display = ("product", "sub_product", "composition_percentage", "active")
    list_filter = ("product", "sub_product", "active")
    autocomplete_fields = ("product", "sub_product")
