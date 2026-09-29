from rest_framework import viewsets

from .models import Machinery
from .serializers import MachinerySerializer


class MachineryViewSet(viewsets.ModelViewSet):
    queryset = Machinery.objects.select_related("store", "unit_power").all()
    serializer_class = MachinerySerializer
    filterset_fields = ("store", "active")
    search_fields = ("machinery", "description")
    ordering_fields = ("machinery", "value_machinery")