# apps/products/product/views.py
from datetime import date
from decimal import Decimal, InvalidOperation

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.units.unit.models import Unit

from .cost import calcular_custo_produto
from .models import Product
from .serializers import ProductSerializer
from .services import (
    ScalingError,
    full_cost,
    scale_product,
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related(
        "store", "sub_category", "sub_category__category"
    ).all()
    serializer_class = ProductSerializer
    filterset_fields = ("store", "sub_category", "active")
    search_fields = ("product", "name_menu", "description_product")
    ordering_fields = ("product", "name_menu")

    @action(detail=True, methods=["get"], url_path="scale")
    def scale(self, request, pk=None):
        """
        GET /api/products/{id}/scale/?quantity=10&unit=8

        Retorna a lista de insumos necessários para produzir `quantity`
        do produto, expressos na unidade padrão de cada insumo.
        """
        product = self.get_object()

        try:
            quantity = Decimal(request.query_params.get("quantity", ""))
        except (InvalidOperation, TypeError):
            return Response(
                {"quantity": "Informe um número válido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        unit_id = request.query_params.get("unit")
        if not unit_id:
            return Response(
                {"unit": "Informe o id da unidade da quantidade alvo."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            unit = Unit.objects.get(pk=unit_id)
        except Unit.DoesNotExist:
            return Response(
                {"unit": f"Unidade {unit_id} não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            scaled = scale_product(product, quantity, unit)
        except ScalingError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({
            "product": product.id,
            "product_name": product.product,
            "target_quantity": str(quantity),
            "target_unit": unit.symbol,
            "ingredients": [
                {
                    "food_ingredient": s.food_ingredient.id,
                    "food_ingredient_name": s.food_ingredient.food_ingredient,
                    "quantity": str(s.quantity),
                    "unit": s.unit.id,
                    "unit_symbol": s.unit.symbol,
                    "unincorporated": s.unincorporated,
                }
                for s in scaled
            ],
        })

    @action(detail=True, methods=["get"], url_path="cost")
    def cost(self, request, pk=None):
        """
        GET /api/products/{id}/cost/?quantity=10&unit=8

        Custo completo de uma produção: insumos + energia + salário.
        """
        product = self.get_object()

        try:
            quantity = Decimal(request.query_params.get("quantity", ""))
        except (InvalidOperation, TypeError):
            return Response(
                {"quantity": "Informe um número válido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        unit_id = request.query_params.get("unit")
        if not unit_id:
            return Response(
                {"unit": "Informe o id da unidade da quantidade alvo."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            unit = Unit.objects.get(pk=unit_id)
        except Unit.DoesNotExist:
            return Response(
                {"unit": f"Unidade {unit_id} não encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            result = full_cost(product, quantity, unit)
        except ScalingError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        def _q(value, places="0.0001"):
            return (
                str(value.quantize(Decimal(places)))
                if value is not None else None
            )

        return Response({
            "product": product.id,
            "product_name": product.product,
            "target_quantity": str(quantity),
            "target_unit": unit.symbol,
            "ingredients": [
                {
                    "food_ingredient": c.food_ingredient.id,
                    "food_ingredient_name": c.food_ingredient.food_ingredient,
                    "quantity": str(c.quantity),
                    "unit": c.unit.id,
                    "unit_symbol": c.unit.symbol,
                    "price_per_unit": str(c.price_per_unit),
                    "subtotal": str(c.subtotal),
                }
                for c in result.ingredients
            ],
            "ingredients_total": str(result.ingredients_total),
            "energy": {
                "total_kwh": str(result.energy.total_kwh),
                "tariff_per_kwh": str(result.energy.tariff_per_kwh),
                "total": str(result.energy.total),
                "steps": result.energy.steps,
            } if result.energy else None,
            "labor": {
                "total_hours": str(result.labor.total_hours),
                "hourly_wage": str(result.labor.hourly_wage),
                "total": str(result.labor.total),
            } if result.labor else None,
            "grand_total": str(result.grand_total),
        })

    @action(detail=True, methods=["get"], url_path="unit-cost")
    def unit_cost(self, request, pk=None):
        """
        GET /api/products/{id}/unit-cost/?data=AAAA-MM-DD

        Devolve o custo unitário do produto (1 unidade) e o
        preço de venda sugerido, com markup e arredondamento.
        """
        produto = self.get_object()
        data_str = request.query_params.get("data")
        try:
            data_ref = date.fromisoformat(data_str) if data_str else None
        except ValueError:
            return Response(
                {"detail": "Parâmetro 'data' inválido. Use AAAA-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        resultado = calcular_custo_produto(produto, data_referencia=data_ref)
        return Response(resultado)