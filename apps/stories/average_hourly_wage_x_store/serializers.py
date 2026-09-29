from rest_framework import serializers

from .models import AverageHourlyWage_x_Store


class AverageHourlyWageXStoreSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name_store", read_only=True)
    unit_symbol = serializers.CharField(source="unit.symbol", read_only=True)

    class Meta:
        model = AverageHourlyWage_x_Store
        fields = (
            "id",
            "store",
            "store_name",
            "average_hourly_wage",
            "unit",
            "unit_symbol",
            "date",
        )