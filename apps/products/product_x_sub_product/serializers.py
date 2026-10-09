# apps/products/product_x_sub_product/serializers.py
from rest_framework import serializers

from .models import Product_x_Sub_Product


class ProductXSubProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.product", read_only=True,
    )
    sub_product_name = serializers.CharField(
        source="sub_product.sub_product", read_only=True,
    )
    relative_to_name = serializers.CharField(
        source="relative_to.sub_product.sub_product",
        read_only=True, allow_null=True,
    )

    class Meta:
        model = Product_x_Sub_Product
        fields = (
            "id",
            "product",
            "product_name",
            "sub_product",
            "sub_product_name",
            "composition_percentage",
            "at_start",
            "at_finish",
            "after_to",
            "relative_to",
            "relative_to_name",
            "elapsed_time",
            "elapsed_signal",
            "active",
        )