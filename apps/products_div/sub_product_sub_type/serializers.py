from rest_framework import serializers

from .models import SubProductSubType


class SubProductSubTypeSerializer(serializers.ModelSerializer):
    sub_product_type_name = serializers.CharField(
        source="sub_product_type.sub_product_type", read_only=True,
    )

    class Meta:
        model = SubProductSubType
        fields = (
            "id",
            "sub_product_sub_type",
            "sub_product_type",
            "sub_product_type_name",
            "active",
        )