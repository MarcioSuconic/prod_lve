#/home/marcio/Desktop/projetos/app_prod_lve/apps/sub_products/sub_product/serializers.py
from rest_framework import serializers

from .models import SubProduct


class SubProductSerializer(serializers.ModelSerializer):
    base_recipe_name = serializers.CharField(source="base_recipe.base_recipe", read_only=True)
    sub_product_sub_type_name = serializers.CharField(
        source="sub_product_sub_type.sub_product_sub_type",
        read_only=True,
    )

    class Meta:
        model = SubProduct
        fields = (
            "id",
            "sub_product",
            "base_recipe",
            "base_recipe_name",
            "sub_product_sub_type",
            "sub_product_sub_type_name",
            "active",
        )