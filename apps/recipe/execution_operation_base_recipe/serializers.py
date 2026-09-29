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
    process_name = serializers.CharField(
        source="operation_execution.operation_base_recipe",
        read_only=True,
    )

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
            "process_name",
            "elapsed_time",
        )

    def validate(self, attrs):
        """
        Roda o clean() do modelo para validar que os três campos de insumo
        (food_ingredient, qtde, unidade) estejam preenchidos em conjunto.
        """
        instance = self.instance or ExecutionOperationBaseRecipe()
        for field, value in attrs.items():
            setattr(instance, field, value)
        instance.clean()
        return attrs