from django.contrib import admin
from .models import ProductCategory


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("category", "active")
    list_filter = ("active",)
    search_fields = ("category",)