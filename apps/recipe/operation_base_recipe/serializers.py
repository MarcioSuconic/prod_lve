from rest_framework import serializers

from .models import OperationBaseRecipe


class ProcessBaseRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationBaseRecipe
        fields = ("id", "operation_base_recipe", "active")