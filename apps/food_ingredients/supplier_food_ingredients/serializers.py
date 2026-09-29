from rest_framework import serializers

from .models import SupplierFoodIngredients


class SupplierFoodIngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierFoodIngredients
        fields = ("id", "supplier", "active")