# /home/marcio/Desktop/projetos/app_prod_lve/apps/units/physical_quantity/views.py
from rest_framework import viewsets

from .models import PhysicalQuantity
from .serializers import PhysicalQuantitySerializer


class PhysicalQuantityViewSet(viewsets.ModelViewSet):
    queryset = PhysicalQuantity.objects.all()
    serializer_class = PhysicalQuantitySerializer
