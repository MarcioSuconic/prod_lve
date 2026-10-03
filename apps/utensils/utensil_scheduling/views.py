from rest_framework import viewsets

from .models import UtensilScheduling
from .serializers import UtensilSchedulingSerializer


class UtensilSchedulingViewSet(viewsets.ModelViewSet):
    queryset = UtensilScheduling.objects.select_related("utensil").all()
    serializer_class = UtensilSchedulingSerializer
    filterset_fields = ("utensil", "active")
    ordering_fields = ("datetime_initial", "datetime_finish")
