from rest_framework import viewsets

from .models import FoodIngredient
from .serializers import FoodIngredientSerializer


class FoodIngredientViewSet(viewsets.ModelViewSet):
    queryset = FoodIngredient.objects.select_related("unit", "supplier").all()
    serializer_class = FoodIngredientSerializer
    filterset_fields = ("supplier", "unit", "active")
    search_fields = ("food_ingredient", "description")
    ordering_fields = ("food_ingredient",)
