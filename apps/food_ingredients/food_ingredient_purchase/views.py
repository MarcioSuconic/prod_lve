from rest_framework import viewsets

from .models import FoodIngredientPurchase
from .serializers import FoodIngredientPurchaseSerializer


class FoodIngredientPurchaseViewSet(viewsets.ModelViewSet):
    queryset = FoodIngredientPurchase.objects.select_related(
        "food_ingredient", "unit"
    ).all()
    serializer_class = FoodIngredientPurchaseSerializer
    filterset_fields = ("food_ingredient", "unit", "date")
    ordering_fields = ("date", "unit_price", "total_price")