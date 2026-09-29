from rest_framework import viewsets

from .models import FoodIngredientPortion
from .serializers import FoodIngredientPortionSerializer


class FoodIngredientPortionViewSet(viewsets.ModelViewSet):
    queryset = FoodIngredientPortion.objects.select_related(
        "food_ingredient", "unit", "reference_unit"
    ).all()
    serializer_class = FoodIngredientPortionSerializer
    filterset_fields = ("food_ingredient", "unit", "reference_unit")
    search_fields = ("food_ingredient__food_ingredient",)
    ordering_fields = ("date", "reference_quantity")