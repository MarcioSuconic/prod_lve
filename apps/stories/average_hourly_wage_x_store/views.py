from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets

from .models import AverageHourlyWage_x_Store
from .serializers import AverageHourlyWageXStoreSerializer


class AverageHourlyWageXStoreViewSet(viewsets.ModelViewSet):
    queryset = AverageHourlyWage_x_Store.objects.select_related("store", "unit").all()
    serializer_class = AverageHourlyWageXStoreSerializer
    filterset_fields = ("store", "date")
    ordering_fields = ("date", "average_hourly_wage")