from rest_framework import mixins, viewsets

from .models import NFPurchase
from .serializers import NFPurchaseSerializer


class NFPurchaseViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        NFPurchase.objects
        .select_related("supplier")
        .prefetch_related("items__food_ingredient", "items__unit")
        .all()
    )
    serializer_class = NFPurchaseSerializer
    filterset_fields = ("supplier", "date")
    search_fields = ("supplier__supplier",)
    ordering_fields = ("date", "total_value")