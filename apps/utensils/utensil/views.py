from rest_framework import viewsets

from .models import Utensil
from .serializers import UtensilSerializer


class UtensilViewSet(viewsets.ModelViewSet):
    queryset = Utensil.objects.select_related("store").all()
    serializer_class = UtensilSerializer
    filterset_fields = ("store", "active")
    search_fields = ("utensil", "code", "description")
    ordering_fields = ("utensil", "code")