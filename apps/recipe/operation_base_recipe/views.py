from rest_framework import viewsets

from .models import OperationBaseRecipe
from .serializers import OperationBaseRecipeSerializer


class OperationBaseRecipeViewSet(viewsets.ModelViewSet):
    queryset = OperationBaseRecipe.objects.all()
    serializer_class = OperationBaseRecipeSerializer
    filterset_fields = ("active",)
    search_fields = ("operation_base_recipe",)
    ordering_fields = ("operation_base_recipe",)
