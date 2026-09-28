from rest_framework import serializers

from .models import Unit


class UnitSerializer(serializers.ModelSerializer):
    physical_quantity_name = serializers.CharField(
        source="physical_quantity.physical_quantity",
        read_only=True,
    )
    physical_quantity_slug = serializers.CharField(
        source="physical_quantity.slug",
        read_only=True,
    )

    class Meta:
        model = Unit
        fields = (
            "id",
            "unit",
            "symbol",
            "physical_quantity",
            "physical_quantity_name",
            "physical_quantity_slug",
            "is_benchmark",
            "conversion_factor",
        )