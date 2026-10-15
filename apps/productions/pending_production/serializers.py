# apps/productions/pending_production/serializers.py
from rest_framework import serializers

from .models import PendingProduction


class PendingProductionSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(
        source="store.name_store", read_only=True,
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True,
    )
    item_count = serializers.IntegerField(
        source="items.count", read_only=True,
    )

    class Meta:
        model = PendingProduction
        fields = (
            "id",
            "store",
            "store_name",
            "status",
            "status_display",
            "scheduled_start",
            "scheduled_end",
            "plan",
            "notes",
            "item_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "created_at",
            "updated_at",
            "scheduled_end",
        )


class PendingProductionListSerializer(serializers.ModelSerializer):
    """
    Serializer enxuto pra listagem (Tela 1 e 2).
    Não devolve o `plan` (que pode ser pesado).
    """
    store_name = serializers.CharField(
        source="store.name_store", read_only=True,
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True,
    )
    item_count = serializers.IntegerField(
        source="items.count", read_only=True,
    )

    class Meta:
        model = PendingProduction
        fields = (
            "id",
            "store",
            "store_name",
            "status",
            "status_display",
            "scheduled_start",
            "notes",
            "item_count",
            "created_at",
        )