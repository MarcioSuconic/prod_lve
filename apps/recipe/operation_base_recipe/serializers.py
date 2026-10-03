#/home/marcio/Desktop/projetos/app_prod_lve/apps/recipe/operation_base_recipe/serializers.py
from rest_framework import serializers

from .models import OperationBaseRecipe


class OperationBaseRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationBaseRecipe
        fields = ("id", "operation_base_recipe", "active")