from rest_framework import serializers

from .models import BaseRecipe


class BaseRecipeSerializer(serializers.ModelSerializer):
    unit_size_symbol = serializers.CharField(source="unit_size.symbol", read_only=True)

    class Meta:
        model = BaseRecipe
        fields = (
            "id",
            "base_recipe",
            "description",
            "size",
            "unit_size",
            "unit_size_symbol",
            "active",
        )