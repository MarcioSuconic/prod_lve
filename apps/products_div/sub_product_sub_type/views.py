from rest_framework import viewsets

from .models import SubProductSubType
from .serializers import SubProductSubTypeSerializer


class SubProductSubTypeViewSet(viewsets.ModelViewSet):
    queryset = SubProductSubType.objects.select_related("sub_product_type").all()
    serializer_class = SubProductSubTypeSerializer
    filterset_fields = ("sub_product_type", "active")
    search_fields = ("sub_product_sub_type",)
    ordering_fields = ("sub_product_sub_type",)

