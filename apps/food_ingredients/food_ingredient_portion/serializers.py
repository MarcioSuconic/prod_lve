#apps/food_ingredients/food_ingredient_portion/serializers.py

from rest_framework import serializers

from .models import FoodIngredientPortion


class FoodIngredientPortionSerializer(serializers.ModelSerializer):
    food_ingredient_name = serializers.CharField(
        source="food_ingredient.food_ingredient",
        read_only=True,
    )
    unit_symbol = serializers.CharField(source="unit.symbol", read_only=True)
    reference_unit_symbol = serializers.CharField(
        source="reference_unit.symbol",
        read_only=True,
    )

    class Meta:
        model = FoodIngredientPortion
        fields = (
            "id",
            "food_ingredient",
            "food_ingredient_name",
            "unit",
            "unit_symbol",
            "reference_quantity",
            "reference_unit",
            "reference_unit_symbol",
            "date",
        )