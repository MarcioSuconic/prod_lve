from django.contrib import admin
from .models import SupplierFoodIngredients


@admin.register(SupplierFoodIngredients)
class SupplierFoodIngredientsAdmin(admin.ModelAdmin):
    list_display = ("supplier", "active")
    list_filter = ("active",)
    search_fields = ("supplier",)
