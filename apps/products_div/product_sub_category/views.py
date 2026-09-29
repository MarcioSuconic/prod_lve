from rest_framework import viewsets

from .models import ProductSubCategory
from .serializers import ProductSubCategorySerializer


class ProductSubCategoryViewSet(viewsets.ModelViewSet):
    queryset = ProductSubCategory.objects.select_related("category").all()
    serializer_class = ProductSubCategorySerializer
    filterset_fields = ("category", "active")
    search_fields = ("sub_category", "description_menu")
    ordering_fields = ("sub_category",)
