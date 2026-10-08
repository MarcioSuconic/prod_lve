from rest_framework import viewsets

from .models import ProductionInput
from .serializers import ProductionInputSerializer


class ProductionInputViewSet(viewsets.ModelViewSet):
    queryset = ProductionInput.objects.select_related(
        "register_production_sub_product",
        "food_ingredient",
        "unit",
    ).all()
    serializer_class = ProductionInputSerializer
    filterset_fields = (
        "register_production_sub_product",
        "food_ingredient",
        "unit",
    )
    ordering_fields = ("food_ingredient", "quantity")
