from django.contrib import admin
from .models import ProductSubCategory


@admin.register(ProductSubCategory)
class ProductSubCategoryAdmin(admin.ModelAdmin):
    list_display = ("sub_category", "category", "active")
    list_filter = ("category", "active")
    search_fields = ("sub_category",)
