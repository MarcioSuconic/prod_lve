# apps/productions/production_x_product/views.py
from rest_framework import viewsets

from .models import ProductionXProduct
from .serializers import ProductionXProductSerializer


class ProductionXProductViewSet(viewsets.ModelViewSet):
    queryset = (
        ProductionXProduct.objects
        .select_related("production", "product", "unit")
        .all()
    )
    serializer_class = ProductionXProductSerializer
    filterset_fields = ("production", "product", "unit", "active")
    ordering_fields = ("production", "product")
