from rest_framework import serializers

from .models import (
    RegisterProductionSubProducts,
    FeedBackProductionSubProducts,
)


class RegisterProductionSubProductsSerializer(serializers.ModelSerializer):
    sub_product_name = serializers.CharField(source="sub_product.sub_product", read_only=True)
    store_name = serializers.CharField(source="store.name_store", read_only=True)
    unit_symbol = serializers.CharField(source="unit.symbol", read_only=True)

    class Meta:
        model = RegisterProductionSubProducts
        fields = (
            "id",
            "sub_product",
            "sub_product_name",
            "store",
            "store_name",
            "date_production",
            "quantity",
            "unit",
            "unit_symbol",
            "done",
        )


class FeedBackProductionSubProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBackProductionSubProducts
        fields = ("id", "register_production_sub_product", "feedback")