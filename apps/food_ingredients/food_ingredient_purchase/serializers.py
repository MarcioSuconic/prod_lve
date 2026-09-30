#/home/marcio/Desktop/projetos/app_prod_lve/apps/food_ingredients/food_ingredient_purchase/serializers.py
from rest_framework import serializers

from .models import FoodIngredientPurchase


class FoodIngredientPurchaseSerializer(serializers.ModelSerializer):
    food_ingredient_name = serializers.CharField(
        source="food_ingredient.food_ingredient", read_only=True,
    )
    unit_symbol = serializers.CharField(source="unit.symbol", read_only=True)
    unit_price = serializers.DecimalField(
        max_digits=20,
        decimal_places=8,
        read_only=True,
    )

    class Meta:
        model = FoodIngredientPurchase
        fields = (
            "id",
            "food_ingredient",
            "food_ingredient_name",
            "date",
            "quantity",
            "unit",
            "unit_symbol",
            "total_price",
            "unit_price",
        )