from rest_framework import serializers

from .models import ElectricPower_x_Store


class ElectricPowerXStoreSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name_store", read_only=True)
    unit_symbol = serializers.CharField(source="unit.symbol", read_only=True)

    class Meta:
        model = ElectricPower_x_Store
        fields = (
            "id",
            "store",
            "store_name",
            "fare_amount_kwh",
            "unit",
            "unit_symbol",
            "date",
        )