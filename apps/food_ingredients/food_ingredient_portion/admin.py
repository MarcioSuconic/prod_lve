from django.contrib import admin

from .models import FoodIngredientPortion


@admin.register(FoodIngredientPortion)
class FoodIngredientPortionAdmin(admin.ModelAdmin):
    list_display = (
        "food_ingredient",
        "unit",
        "reference_quantity",
        "reference_unit",
        "date",
    )
    list_filter = ("food_ingredient", "unit", "reference_unit", "date")
    search_fields = ("food_ingredient__food_ingredient",)
    date_hierarchy = "date"
    autocomplete_fields = ("food_ingredient",)