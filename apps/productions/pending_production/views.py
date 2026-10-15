# apps/productions/pending_production/views.py

from django.conf import settings
from django.http import FileResponse
from pathlib import Path

from .pdf import gerar_pdf_lista_compras

from datetime import datetime

from django.http import FileResponse
from pathlib import Path
from django.conf import settings

from .pdf import gerar_pdf_lista_compras

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.productions.production_x_product.models import (
    ProductionXProduct,
)
from apps.productions.production_x_product.serializers import (
    ProductionXProductSerializer,
)

from .models import PendingProduction
from .serializers import (
    PendingProductionListSerializer,
    PendingProductionSerializer,
)
from apps.productions.pending_production.services import (
    ProductionPlanError,
    calcular_plano_producao,
)

class PendingProductionViewSet(viewsets.ModelViewSet):
    queryset = (
        PendingProduction.objects
        .select_related("store")
        .prefetch_related("items__product", "items__unit")
        .all()
    )
    filterset_fields = ("store", "status")
    ordering_fields = ("created_at", "scheduled_start", "status")
    
    @action(detail=True, methods=["post"], url_path="shopping-list.pdf")
    def shopping_list_pdf(self, request, pk=None):
        """
        POST /api/pending-productions/{id}/shopping-list.pdf/

        Gera o PDF da lista de compras de uma produção planejada.
        """
        try:
            info = gerar_pdf_lista_compras(int(pk))
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        arquivo = Path(info["file"])
        if not arquivo.exists():
            return Response(
                {"detail": "Arquivo PDF não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return FileResponse(
            open(arquivo, "rb"),
            as_attachment=False,
            filename=info["filename"],
            content_type="application/pdf",
        )

    @action(detail=True, methods=["post"], url_path="shopping-list.pdf")
    def shopping_list_pdf(self, request, pk=None):
        try:
            info = gerar_pdf_lista_compras(int(pk))
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        arquivo = Path(info["file"])
        if not arquivo.exists():
            return Response(
                {"detail": "Arquivo PDF não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return FileResponse(
            open(arquivo, "rb"),
            as_attachment=False,
            filename=info["filename"],
            content_type="application/pdf",
        )

    def get_serializer_class(self):
        if self.action == "list":
            return PendingProductionListSerializer
        return PendingProductionSerializer

    def create(self, request, *args, **kwargs):
        """
        Cria uma produção pendente com itens opcionais.

        Consolida itens com mesmo (product, unit), somando as quantidades.
        """
        data = request.data.copy()
        items = data.pop("items", [])

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        production = serializer.save()

        # Consolida por (product, unit)
        consolidado = {}
        for item in items:
            key = (item["product"], item["unit"])
            if key not in consolidado:
                consolidado[key] = {
                    "product": item["product"],
                    "unit": item["unit"],
                    "quantity": 0.0,
                }
            try:
                consolidado[key]["quantity"] += float(item["quantity"])
            except (ValueError, TypeError):
                # Se não for numérico, ignora
                pass

        for v in consolidado.values():
            ProductionXProduct.objects.create(
                production=production,
                product_id=v["product"],
                quantity=f'{v["quantity"]:.3f}',
                unit_id=v["unit"],
            )

        return Response(
            PendingProductionSerializer(production).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="add-item")
    def add_item(self, request, pk=None):
        """
        Adiciona um item à produção.

        Payload:
            {"product": 1, "quantity": "50", "unit": 2}
        """
        production = self.get_object()
        if production.status != "pending":
            return Response(
                {"detail": "Só é possível adicionar itens em produções "
                           "com status 'pending'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ProductionXProductSerializer(data={
            "production": production.id,
            **request.data,
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="remove-item")
    def remove_item(self, request, pk=None):
        """
        Remove um item da produção.

        Payload:
            {"item_id": 1}
        """
        production = self.get_object()
        item_id = request.data.get("item_id")
        if not item_id:
            return Response(
                {"item_id": "Obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            item = production.items.get(id=item_id)
        except ProductionXProduct.DoesNotExist:
            return Response(
                {"detail": f"Item {item_id} não encontrado."},
                status=status.HTTP_404_NOT_FOUND,
            )
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=["post"], url_path="plan")
    def plan(self, request, pk=None):
        """
        POST /api/pending-productions/{id}/plan/

        Calcula o plano de produção e salva no registro.

        Payload:
            {
                "scheduled_start": "2026-10-16T08:00:00"
            }
        """
        production = self.get_object()

        if production.status not in ("pending", "scheduled"):
            return Response(
                {"detail": (
                    f"Só é possível planejar produções com status "
                    f"'pending' ou 'scheduled'. Status atual: "
                    f"'{production.status}'."
                )},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Data/hora (opcional no payload; usa a existente se não vier)
        start_str = request.data.get("scheduled_start")
        if start_str:
            try:
                scheduled_start = datetime.fromisoformat(start_str)
            except ValueError:
                return Response(
                    {"scheduled_start": (
                        "Formato inválido. Use AAAA-MM-DDTHH:MM:SS."
                    )},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            scheduled_start = production.scheduled_start
            if not scheduled_start:
                return Response(
                    {"scheduled_start": (
                        "Obrigatório. Informe a data/hora de início."
                    )},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Salva o start antes de calcular (o serviço lê do objeto)
        production.scheduled_start = scheduled_start
        production.save(update_fields=["scheduled_start", "updated_at"])

        # Calcula
        try:
            plano = calcular_plano_producao(production.id)
        except ProductionPlanError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Salva no registro
        production.plan = plano
        production.status = "scheduled"
        production.scheduled_end = datetime.fromisoformat(plano["data_fim"])
        production.save(update_fields=[
            "plan", "status", "scheduled_end", "updated_at",
        ])

        return Response(plano)
