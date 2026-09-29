from rest_framework import viewsets

from .models import ProductCategory
from .serializers import ProductCategorySerializer


class ProductCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    filterset_fields = ("active",)
    search_fields = ("category", "description_menu")
    ordering_fields = ("category",)
