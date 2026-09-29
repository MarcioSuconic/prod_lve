from rest_framework import viewsets

from .models import SupplierFoodIngredients
from .serializers import SupplierFoodIngredientsSerializer


class SupplierFoodIngredientsViewSet(viewsets.ModelViewSet):
    queryset = SupplierFoodIngredients.objects.all()
    serializer_class = SupplierFoodIngredientsSerializer
    filterset_fields = ("active",)
    search_fields = ("supplier",)
    ordering_fields = ("supplier",)
