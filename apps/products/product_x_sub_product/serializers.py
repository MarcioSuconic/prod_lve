#/home/marcio/Desktop/projetos/app_prod_lve/apps/products/product_x_sub_product/serializers.py
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
            "composition_percentage",
            "active",
        )