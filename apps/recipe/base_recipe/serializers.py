#/home/marcio/Desktop/projetos/app_prod_lve/apps/recipe/base_recipe/serializers.py
from django.db import transaction
from rest_framework import serializers

from apps.recipe.execution_operation_base_recipe.models import (
    ExecutionOperationBaseRecipe,
)

from .models import BaseRecipe


class BaseRecipeSerializer(serializers.ModelSerializer):
    unit_size_symbol = serializers.CharField(
        source="unit_size.symbol", read_only=True,
    )

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


class BaseRecipeReplaceExecutionItemSerializer(serializers.ModelSerializer):
    """
    Item de execução dentro do replace ou do create. Não expõe nome/código
    (só serve para escrita), e não aceita `base_recipe` — ele é injetado
    pelo pai.
    """
    class Meta:
        model = ExecutionOperationBaseRecipe
        fields = (
            "stage_execution",
            "operation_execution",
            "description_execution",
            "food_ingredient",
            "qtde_food_ingredient",
            "unidade_qtde_food_ingredient",
            "incorporation_percentage",
            "temperature",           # ← NOVO
            "pH",
            "execution_time",
            "elapsed_time",
            "machinery",
            "utensils",
        )


class BaseRecipeReplaceSerializer(serializers.ModelSerializer):
    """
    Cria ou substitui uma BaseRecipe e todas as suas execuções,
    em uma única transação.
    """
    executions = BaseRecipeReplaceExecutionItemSerializer(
        many=True, write_only=True,
    )

    class Meta:
        model = BaseRecipe
        fields = (
            "id",
            "base_recipe",
            "description",
            "size",
            "unit_size",
            "active",
            "executions",
        )
        read_only_fields = ("id",)

    def validate_executions(self, value):
        if not value:
            raise serializers.ValidationError(
                "A receita precisa ter pelo menos uma execução."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        executions_data = validated_data.pop("executions", [])
        instance = BaseRecipe.objects.create(**validated_data)
        for exec_data in executions_data:
            ExecutionOperationBaseRecipe.objects.create(
                base_recipe=instance,
                **exec_data,
            )
        return instance

    @transaction.atomic
    def update(self, instance, validated_data):
        executions_data = validated_data.pop("executions", [])

        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()

        ExecutionOperationBaseRecipe.objects.filter(
            base_recipe=instance,
        ).delete()

        for exec_data in executions_data:
            ExecutionOperationBaseRecipe.objects.create(
                base_recipe=instance,
                **exec_data,
            )

        return instance