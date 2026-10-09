# apps/products/product/views.py
import re
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.conf import settings
from django.http import FileResponse
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
from .tech_sheet import _slug, gerar_ficha_tecnica
from datetime import datetime
from .services import ScheduleError, calcular_cronograma

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related(
        "store", "sub_category", "sub_category__category"
    ).all()
    serializer_class = ProductSerializer
    filterset_fields = ("store", "sub_category", "active")
    search_fields = ("product", "name_menu", "description_product")
    ordering_fields = ("product", "name_menu")

    # ------------------------------------------------------------------
    # /scale/ — lista de insumos para uma produção
    # ------------------------------------------------------------------
    @action(detail=True, methods=["get"], url_path="scale")
    def scale(self, request, pk=None):
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

    # ------------------------------------------------------------------
    # /cost/ — custo completo de uma produção
    # ------------------------------------------------------------------
    @action(detail=True, methods=["get"], url_path="cost")
    def cost(self, request, pk=None):
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

    # ------------------------------------------------------------------
    # /unit-cost/ — custo unitário + preço com markup
    # ------------------------------------------------------------------
    @action(detail=True, methods=["get"], url_path="unit-cost")
    def unit_cost(self, request, pk=None):
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

    # ------------------------------------------------------------------
    # /tech-sheet/ (POST) — gera nova versão da ficha técnica
    # ------------------------------------------------------------------
    @action(detail=True, methods=["post"], url_path="tech-sheet")
    def tech_sheet_generate(self, request, pk=None):
        produto = self.get_object()
        try:
            info = gerar_ficha_tecnica(produto)
        except Exception as e:
            return Response(
                {"detail": f"Erro ao gerar ficha: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(info, status=status.HTTP_201_CREATED)

    # ------------------------------------------------------------------
    # /tech-sheet/ (GET) — baixa o PDF da ficha técnica
    # ------------------------------------------------------------------
    @action(detail=True, methods=["get"], url_path="tech-sheet/download")
    def tech_sheet_download(self, request, pk=None):
        produto = self.get_object()
        pasta = Path(settings.MEDIA_ROOT) / "tech_sheets"
        slug = _slug(produto.product)

        version = request.query_params.get("version")
        if version:
            arquivo = pasta / f"{slug}_v{version}.pdf"
        else:
            existentes = []
            if pasta.exists():
                existentes = sorted(
                    pasta.glob(f"{slug}_v*.pdf"),
                    key=lambda p: int(
                        re.search(r"_v(\d+)\.pdf$", p.name).group(1)
                    ),
                )
            if not existentes:
                return Response(
                    {"detail": "Nenhuma ficha técnica gerada ainda."},
                    status=status.HTTP_404_NOT_FOUND,
                )
            arquivo = existentes[-1]

        if not arquivo.exists():
            return Response(
                {"detail": f"Arquivo {arquivo.name} não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return FileResponse(
            open(arquivo, "rb"),
            as_attachment=False,
            filename=arquivo.name,
            content_type="application/pdf",
        )
        
    @action(detail=True, methods=["get"], url_path="schedule")
    def schedule(self, request, pk=None):
        """
        GET /api/products/{id}/schedule/?start=AAAA-MM-DDTHH:MM:SS

        Calcula o cronograma de produção a partir de uma data/hora.
        """
        produto = self.get_object()
        start_str = request.query_params.get("start")
        if not start_str:
            return Response(
                {"start": "Informe a data/hora de início (formato ISO 8601)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            data_inicio = datetime.fromisoformat(start_str)
        except ValueError:
            return Response(
                {"start": "Formato inválido. Use AAAA-MM-DDTHH:MM:SS."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            resultado = calcular_cronograma(produto.id, data_inicio)
        except ScheduleError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(resultado)