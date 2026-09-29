from rest_framework import viewsets

from .models import SubProduct
from .serializers import SubProductSerializer


class SubProductViewSet(viewsets.ModelViewSet):
    queryset = SubProduct.objects.select_related(
        "base_recipe", "sub_product_sub_type"
    ).all()
    serializer_class = SubProductSerializer
    filterset_fields = ("base_recipe", "sub_product_sub_type", "active")
    search_fields = ("sub_product",)
    ordering_fields = ("sub_product",)