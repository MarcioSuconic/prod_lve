from rest_framework import serializers

from .models import Product_x_Sub_Product


class ProductXSubProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.product", read_only=True)
    sub_product_name = serializers.CharField(source="sub_product.sub_product", read_only=True)

    class Meta:
        model = Product_x_Sub_Product
        fields = (
            "id",
            "product",
            "product_name",
            "sub_product",
            "sub_product_name",
            "bakers_percentage",
            "active",
        )