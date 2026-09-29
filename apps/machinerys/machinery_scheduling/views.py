from rest_framework import viewsets

from .models import MachineryScheduling
from .serializers import MachinerySchedulingSerializer


class MachinerySchedulingViewSet(viewsets.ModelViewSet):
    queryset = MachineryScheduling.objects.select_related("machinery").all()
    serializer_class = MachinerySchedulingSerializer
    filterset_fields = ("machinery", "active")
    ordering_fields = ("datetime_initial", "datetime_finish")
