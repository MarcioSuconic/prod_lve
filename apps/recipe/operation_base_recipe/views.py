from rest_framework import viewsets

from .models import OperationBaseRecipe
from .serializers import ProcessBaseRecipeSerializer


class ProcessBaseRecipeViewSet(viewsets.ModelViewSet):
    queryset = OperationBaseRecipe.objects.all()
    serializer_class = ProcessBaseRecipeSerializer
    filterset_fields = ("active",)
    search_fields = ("operation_base_recipe",)
    ordering_fields = ("operation_base_recipe",)
