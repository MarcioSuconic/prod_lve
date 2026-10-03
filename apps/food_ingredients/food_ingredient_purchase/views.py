# /home/marcio/Desktop/projetos/app_prod_lve/apps/food_ingredients/food_ingredient_purchase/views.py
from rest_framework import viewsets

from .models import FoodIngredientPurchase
from .serializers import FoodIngredientPurchaseSerializer


class FoodIngredientPurchaseViewSet(viewsets.ModelViewSet):
    queryset = FoodIngredientPurchase.objects.select_related(
        "nf", "food_ingredient", "unit"
    ).all()
    filterset_fields = ("nf", "food_ingredient", "unit", "date")
    ordering_fields = ("date", "total_price")
    serializer_class = FoodIngredientPurchaseSerializer
