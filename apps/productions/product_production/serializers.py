from rest_framework import serializers

from .models import RegisterProductionProducts, FeedBackProductionProducts


class RegisterProductionProductsSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.product", read_only=True)
    unit_symbol = serializers.CharField(source="unit.symbol", read_only=True)

    class Meta:
        model = RegisterProductionProducts
        fields = (
            "id",
            "product",
            "product_name",
            "date_production",
            "quantity",
            "unit",
            "unit_symbol",
            "done",
        )


class FeedBackProductionProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBackProductionProducts
        fields = ("id", "register_production_product", "feedback")