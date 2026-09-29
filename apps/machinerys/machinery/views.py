from rest_framework import viewsets

from .models import Machinery, Utensil
from .serializers import MachinerySerializer, UtensilSerializer


class MachineryViewSet(viewsets.ModelViewSet):
    queryset = Machinery.objects.select_related("store", "unit_power").all()
    serializer_class = MachinerySerializer
    filterset_fields = ("store", "active")
    search_fields = ("machinery", "code", "description")
    ordering_fields = ("machinery", "code", "value_machinery")


class UtensilViewSet(viewsets.ModelViewSet):
    queryset = Utensil.objects.select_related("store").all()
    serializer_class = UtensilSerializer
    filterset_fields = ("store", "active")
    search_fields = ("utensil", "code", "description")
    ordering_fields = ("utensil", "code")