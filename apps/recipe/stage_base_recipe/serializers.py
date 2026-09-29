from rest_framework import serializers

from .models import StageBaseRecipe


class StageBaseRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StageBaseRecipe
        fields = ("id", "stage_base_recipe", "active")