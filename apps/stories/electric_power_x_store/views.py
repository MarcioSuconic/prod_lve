from rest_framework import viewsets

from .models import ElectricPower_x_Store
from .serializers import ElectricPowerXStoreSerializer


class ElectricPowerXStoreViewSet(viewsets.ModelViewSet):
    queryset = ElectricPower_x_Store.objects.select_related("store", "unit").all()
    serializer_class = ElectricPowerXStoreSerializer
    filterset_fields = ("store", "date")
    ordering_fields = ("date", "fare_amount_kwh")
