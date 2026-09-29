from rest_framework import viewsets

from .models import BaseRecipe
from .serializers import BaseRecipeSerializer


class BaseRecipeViewSet(viewsets.ModelViewSet):
    queryset = BaseRecipe.objects.select_related("unit_size").all()
    serializer_class = BaseRecipeSerializer
    filterset_fields = ("unit_size", "active")
    search_fields = ("base_recipe", "description")
    ordering_fields = ("base_recipe", "size")
