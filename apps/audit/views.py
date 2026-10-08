from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .services import auditar_sistema


class AuditViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="full")
    def full(self, request):
        return Response(auditar_sistema())

    @action(detail=False, methods=["get"], url_path="startup")
    def startup(self, request):
        """Versão enxuta (só os totais) pra mostrar no startup."""
        r = auditar_sistema()
        return Response({
            "produtos_sem_100": len(r["produtos_sem_100"]),
            "insumos_sem_densidade": len(r["insumos_sem_densidade"]),
            "receitas_com_balanco_ruim": len(r["receitas_com_balanco_ruim"]),
        })