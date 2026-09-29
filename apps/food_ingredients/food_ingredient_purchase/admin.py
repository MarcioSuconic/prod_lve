from django.contrib import admin

from .models import FoodIngredientPurchase


@admin.register(FoodIngredientPurchase)
class FoodIngredientPurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "food_ingredient",
        "date",
        "quantity",
        "unit",
        "total_price",
        "unit_price",
    )
    list_filter = ("food_ingredient", "unit", "date")
    search_fields = ("food_ingredient__food_ingredient",)
    date_hierarchy = "date"
    autocomplete_fields = ("food_ingredient",)

    @admin.display(description="preço por unidade")
    def unit_price(self, obj):
        return f"{obj.unit_price:.6f}"
