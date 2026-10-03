#/home/marcio/Desktop/projetos/app_prod_lve/apps/units/physical_quantity/serializers.py
from rest_framework import serializers

from .models import PhysicalQuantity


class PhysicalQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PhysicalQuantity
        fields = ("id", "physical_quantity", "slug")
        read_only_fields = ("slug",)