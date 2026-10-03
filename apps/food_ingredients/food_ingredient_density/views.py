#/home/marcio/Desktop/projetos/app_prod_lve/apps/food_ingredients/food_ingredient_density/views.py
from rest_framework import viewsets

from .models import FoodIngredientDensity
from .serializers import FoodIngredientDensitySerializer


class FoodIngredientDensityViewSet(viewsets.ModelViewSet):
    queryset = FoodIngredientDensity.objects.select_related(
        "food_ingredient", "mass_unit", "volume_unit"
    ).all()
    serializer_class = FoodIngredientDensitySerializer
    filterset_fields = ("food_ingredient", "mass_unit", "volume_unit")
    search_fields = ("food_ingredient__food_ingredient",)
    ordering_fields = ("density", "date", "reference_temperature_celsius")