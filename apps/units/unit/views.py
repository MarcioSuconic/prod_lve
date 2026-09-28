from rest_framework import viewsets

from .models import Unit
from .serializers import UnitSerializer


class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.select_related("physical_quantity").all()
    serializer_class = UnitSerializer
    filterset_fields = ("physical_quantity", "is_benchmark")
    search_fields = ("unit", "symbol")
    ordering_fields = ("unit", "physical_quantity", "conversion_factor")