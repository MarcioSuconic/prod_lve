# apps/productions/production_x_product/serializers.py
from rest_framework import serializers

from .models import ProductionXProduct


class ProductionXProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.product", read_only=True,
    )
    unit_symbol = serializers.CharField(
        source="unit.symbol", read_only=True,
    )

    class Meta:
        model = ProductionXProduct
        fields = (
            "id",
            "production",
            "product",
            "product_name",
            "quantity",
            "unit",
            "unit_symbol",
            "active",
        )