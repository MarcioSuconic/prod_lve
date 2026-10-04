from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import BaseRecipe
from .serializers import (
    BaseRecipeReplaceSerializer,
    BaseRecipeSerializer,
)


class BaseRecipeViewSet(viewsets.ModelViewSet):
    queryset = BaseRecipe.objects.select_related("unit_size").all()
    serializer_class = BaseRecipeSerializer
    filterset_fields = ("unit_size", "active")
    search_fields = ("base_recipe", "description")
    ordering_fields = ("base_recipe", "size")

    def get_serializer_class(self):
        """
        - `create` e `replace-executions`: usam o serializer que aceita
          `executions` embutidas (cabeçalho + passos).
        - Todo o resto: serializer normal.
        """
        if self.action in ("create", "replace_executions"):
            return BaseRecipeReplaceSerializer
        return BaseRecipeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        # Devolve a receita com os dados do serializer padrão
        return Response(
            BaseRecipeSerializer(instance).data,
            status=201,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="replace-executions",
        serializer_class=BaseRecipeReplaceSerializer,
    )
    def replace_executions(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=False,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(BaseRecipeSerializer(instance).data)
