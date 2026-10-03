#/home/marcio/Desktop/projetos/app_prod_lve/apps/food_ingredients/food_ingredient_density/serializers.py
from rest_framework import serializers

from .models import FoodIngredientDensity


class FoodIngredientDensitySerializer(serializers.ModelSerializer):
    food_ingredient_name = serializers.CharField(
        source="food_ingredient.food_ingredient",
        read_only=True,
    )
    mass_unit_symbol = serializers.CharField(source="mass_unit.symbol", read_only=True)
    volume_unit_symbol = serializers.CharField(source="volume_unit.symbol", read_only=True)

    class Meta:
        model = FoodIngredientDensity
        fields = (
            "id",
            "food_ingredient",
            "food_ingredient_name",
            "density",
            "mass_unit",
            "mass_unit_symbol",
            "volume_unit",
            "volume_unit_symbol",
            "reference_temperature_celsius",
            "date",
        )