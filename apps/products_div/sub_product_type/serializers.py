from rest_framework import serializers

from .models import SubProductType


class SubProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubProductType
        fields = ("id", "sub_product_type", "active")