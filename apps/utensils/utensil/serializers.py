#/home/marcio/Desktop/projetos/app_prod_lve/apps/utensils/utensil/serializers.py
from rest_framework import serializers

from .models import Utensil


class UtensilSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source="store.name_store", read_only=True)

    class Meta:
        model = Utensil
        fields = (
            "id",
            "code",
            "utensil",
            "description",
            "value_utensil",
            "store",
            "store_name",
            "active",
        )