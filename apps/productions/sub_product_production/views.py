from rest_framework import viewsets

from .models import (
    RegisterProductionSubProducts,
    FeedBackProductionSubProducts,
)
from .serializers import (
    RegisterProductionSubProductsSerializer,
    FeedBackProductionSubProductsSerializer,
)


class RegisterProductionSubProductsViewSet(viewsets.ModelViewSet):
    queryset = RegisterProductionSubProducts.objects.select_related(
        "sub_product", "store", "unit"
    ).all()
    serializer_class = RegisterProductionSubProductsSerializer
    filterset_fields = ("store", "sub_product", "done", "unit")
    ordering_fields = ("date_production", "quantity")


class FeedBackProductionSubProductsViewSet(viewsets.ModelViewSet):
    queryset = FeedBackProductionSubProducts.objects.select_related(
        "register_production_sub_product"
    ).all()
    serializer_class = FeedBackProductionSubProductsSerializer
    filterset_fields = ("register_production_sub_product",)
