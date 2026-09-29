from rest_framework import viewsets

from .models import Product_x_Sub_Product
from .serializers import ProductXSubProductSerializer


class ProductXSubProductViewSet(viewsets.ModelViewSet):
    queryset = Product_x_Sub_Product.objects.select_related(
        "product", "sub_product"
    ).all()
    serializer_class = ProductXSubProductSerializer
    filterset_fields = ("product", "sub_product", "active")
    ordering_fields = ("product", "sub_product", "bakers_percentage")
