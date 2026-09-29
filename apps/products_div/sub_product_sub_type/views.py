from rest_framework import viewsets

from .models import SubProductSubType
from .serializers import SubProductSubTypeSerializer


class SubProductSubTypeViewSet(viewsets.ModelViewSet):
    queryset = SubProductSubType.objects.select_related("type").all()
    serializer_class = SubProductSubTypeSerializer
    filterset_fields = ("type", "active")
    search_fields = ("sub_product_sub_type",)
    ordering_fields = ("sub_product_sub_type",)
