from rest_framework import serializers

from .models import ProductionInput


class ProductionInputSerializer(serializers.ModelSerializer):
    food_ingredient_name = serializers.CharField(
        source="food_ingredient.food_ingredient", read_only=True,
    )
    unit_symbol = serializers.CharField(source="unit.symbol", read_only=True)

    class Meta:
        model = ProductionInput
        fields = (
            "id",
            "register_production_sub_product",
            "food_ingredient",
            "food_ingredient_name",
            "quantity",
            "unit",
            "unit_symbol",
            "cost",
        )