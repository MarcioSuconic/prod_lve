# apps/recipe/base_recipe/views.py
from datetime import date

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import BaseRecipe
from .serializers import (
    BaseRecipeReplaceSerializer,
    BaseRecipeSerializer,
)
from .services import calcular_custo_receita

from .services import calcular_balanco_massa
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

    @action(detail=True, methods=["get"], url_path="cost")
    def cost(self, request, pk=None):
        """
        GET /api/base-recipes/{id}/cost/?data=AAAA-MM-DD

        Devolve o custo detalhado da receita (insumos + energia + mão de obra)
        por passo e no total. Margem/preço ficam no cliente.
        """
        receita = self.get_object()
        data_str = request.query_params.get("data")
        try:
            data_ref = date.fromisoformat(data_str) if data_str else None
        except ValueError:
            return Response(
                {"detail": "Parâmetro 'data' inválido. Use AAAA-MM-DD."},
                status=400,
            )
            
        resultado = calcular_custo_receita(receita, data_referencia=data_ref)
        resultado["balanco"] = calcular_balanco_massa(receita, data_referencia=data_ref)
        return Response(resultado)