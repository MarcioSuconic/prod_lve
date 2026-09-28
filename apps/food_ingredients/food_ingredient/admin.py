from django.contrib import admin
from .models import FoodIngredient


@admin.register(FoodIngredient)
class FoodIngredientAdmin(admin.ModelAdmin):
    list_display = ("food_ingredient", "unit", "supplier", "active")
    list_filter = ("supplier", "unit", "active")
    search_fields = ("food_ingredient",)