#/home/marcio/Desktop/projetos/app_prod_lve/apps/food_ingredients/food_ingredient_density/admin.py
from django.contrib import admin

from .models import FoodIngredientDensity


@admin.register(FoodIngredientDensity)
class FoodIngredientDensityAdmin(admin.ModelAdmin):
    list_display = (
        "food_ingredient",
        "density",
        "mass_unit",
        "volume_unit",
        "reference_temperature_celsius",
        "date",
    )
    list_filter = ("food_ingredient", "reference_temperature_celsius", "date")
    search_fields = ("food_ingredient__food_ingredient",)
    date_hierarchy = "date"
    autocomplete_fields = ("food_ingredient",)