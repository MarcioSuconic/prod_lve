#/home/marcio/Desktop/projetos/app_prod_lve/apps/recipe/execution_operation_base_recipe/serializers.py
from rest_framework import serializers

from .models import ExecutionOperationBaseRecipe


class ExecutionOperationBaseRecipeSerializer(serializers.ModelSerializer):
    food_ingredient_name = serializers.CharField(
        source="food_ingredient.food_ingredient",
        read_only=True,
        allow_null=True,
    )
    unidade_symbol = serializers.CharField(
        source="unidade_qtde_food_ingredient.symbol",
        read_only=True,
        allow_null=True,
    )
    stage_name = serializers.CharField(
        source="stage_execution.stage_base_recipe",
        read_only=True,
    )
    operation_name = serializers.CharField(
        source="operation_execution.operation_base_recipe",
        read_only=True,
    )
    machinery_name = serializers.CharField(
        source="machinery.machinery",
        read_only=True,
        allow_null=True,
    )
    machinery_code = serializers.CharField(
        source="machinery.code",
        read_only=True,
        allow_null=True,
    )
    utensil_details = serializers.SerializerMethodField()

    class Meta:
        model = ExecutionOperationBaseRecipe
        fields = (
            "id",
            "base_recipe",
            "description_execution",
            "food_ingredient",
            "food_ingredient_name",
            "qtde_food_ingredient",
            "unidade_qtde_food_ingredient",
            "unidade_symbol",
            "unincorporated_ingredient",
            "stage_execution",
            "stage_name",
            "operation_execution",
            "operation_name",
            "elapsed_time",
            "machinery",
            "machinery_name",
            "machinery_code",
            "utensils",
            "utensil_details",
        )

    def get_utensil_details(self, obj):
        return [
            {"id": u.id, "code": u.code, "utensil": u.utensil}
            for u in obj.utensils.all()
        ]

    def validate(self, attrs):
        instance = self.instance or ExecutionOperationBaseRecipe()
        for field, value in attrs.items():
            if field == "utensils":
                continue  # M2M — não pode setar direto no clean()
            setattr(instance, field, value)
        instance.clean()
        return attrs