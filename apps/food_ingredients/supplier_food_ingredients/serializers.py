#/home/marcio/Desktop/projetos/app_prod_lve/apps/food_ingredients/supplier_food_ingredients/serializers.py
from rest_framework import serializers

from .models import SupplierFoodIngredients


class SupplierFoodIngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplierFoodIngredients
        fields = ("id", "supplier", "active")