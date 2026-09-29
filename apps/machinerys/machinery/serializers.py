from rest_framework import serializers

from .models import Machinery


class MachinerySerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name_store", read_only=True)
    unit_power_symbol = serializers.CharField(source="unit_power.symbol", read_only=True)

    class Meta:
        model = Machinery
        fields = (
            "id",
            "machinery",
            "description",
            "qtde_power",
            "unit_power",
            "unit_power_symbol",
            "value_machinery",
            "store",
            "store_name",
            "active",
        )