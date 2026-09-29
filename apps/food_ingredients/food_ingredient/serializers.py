from rest_framework import serializers

from .models import FoodIngredient


class FoodIngredientSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source="unit.unit", read_only=True)
    unit_symbol = serializers.CharField(source="unit.symbol", read_only=True)
    supplier_name = serializers.CharField(source="supplier.supplier", read_only=True)

    class Meta:
        model = FoodIngredient
        fields = (
            "id",
            "food_ingredient",
            "description",
            "qtde_default_shopping",
            "unit",
            "unit_name",
            "unit_symbol",
            "supplier",
            "supplier_name",
            "active",
        )

    def validate(self, attrs):
        """
        Roda o clean() do modelo para aplicar a regra de densidade obrigatória
        quando a unidade padrão for de volume.
        """
        instance = self.instance or FoodIngredient()
        for field, value in attrs.items():
            setattr(instance, field, value)
        instance.clean()
        return attrs