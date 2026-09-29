from decimal import Decimal, InvalidOperation

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from apps.units.unit.models import Unit
from .models import Product
from .serializers import ProductSerializer
from .services import scale_product, ScalingError

from .services import scale_product, ingredient_cost, ScalingError


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

        Retorna o custo dos insumos para produzir `quantity` do produto.
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
            costs = ingredient_cost(product, quantity, unit)
        except ScalingError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total = sum((c.subtotal for c in costs), Decimal("0"))

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
                for c in costs
            ],
            "ingredients_total": str(total),
        })