from rest_framework import viewsets

from .models import ExecutionOperationBaseRecipe
from .serializers import ExecutionOperationBaseRecipeSerializer


class ExecutionOperationBaseRecipeViewSet(viewsets.ModelViewSet):
    queryset = ExecutionOperationBaseRecipe.objects.select_related(
        "base_recipe",
        "food_ingredient",
        "unidade_qtde_food_ingredient",
        "stage_execution",
        "operation_execution",
    ).all()
    serializer_class = ExecutionOperationBaseRecipeSerializer
    filterset_fields = (
        "base_recipe",
        "stage_execution",
        "operation_execution",
        "food_ingredient",
    )
    search_fields = ("description_execution",)
    ordering_fields = ("base_recipe", "stage_execution", "operation_execution")
