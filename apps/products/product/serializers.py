from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name_store", read_only=True)
    sub_category_name = serializers.CharField(source="sub_category.sub_category", read_only=True)
    category_name = serializers.CharField(source="sub_category.category.category", read_only=True)
    unit_weight_or_volume_symbol = serializers.CharField(
        source="unit_weight_or_volume.symbol", read_only=True,
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "product",
            "description_product",
            "name_menu",
            "description_menu",
            "product_weight_or_volume",           # ← está faltando?
            "unit_weight_or_volume",               # ← está faltando?
            "unit_weight_or_volume_symbol",        # ← adicionar
            "store",
            "store_name",
            "sub_category",
            "sub_category_name",
            "category_name",
            "active",
        )