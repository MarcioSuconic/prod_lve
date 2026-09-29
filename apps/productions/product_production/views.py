from rest_framework import viewsets

from .models import RegisterProductionProducts, FeedBackProductionProducts
from .serializers import (
    RegisterProductionProductsSerializer,
    FeedBackProductionProductsSerializer,
)


class RegisterProductionProductsViewSet(viewsets.ModelViewSet):
    queryset = RegisterProductionProducts.objects.select_related("product", "unit").all()
    serializer_class = RegisterProductionProductsSerializer
    filterset_fields = ("product", "done", "unit")
    ordering_fields = ("date_production", "quantity")


class FeedBackProductionProductsViewSet(viewsets.ModelViewSet):
    queryset = FeedBackProductionProducts.objects.select_related(
        "register_production_product"
    ).all()
    serializer_class = FeedBackProductionProductsSerializer
    filterset_fields = ("register_production_product",)
