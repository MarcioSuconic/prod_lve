from rest_framework import viewsets

from .models import SubProductType
from .serializers import SubProductTypeSerializer


class SubProductTypeViewSet(viewsets.ModelViewSet):
    queryset = SubProductType.objects.all()
    serializer_class = SubProductTypeSerializer
    filterset_fields = ("active",)
    search_fields = ("sub_product_type",)
    ordering_fields = ("sub_product_type",)
