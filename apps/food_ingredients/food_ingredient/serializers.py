from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from apps.food_ingredients.food_ingredient_density.models import (
    FoodIngredientDensity,
)
from apps.units.unit.models import Unit

from .models import FoodIngredient


class FoodIngredientSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source="unit.unit", read_only=True)
    unit_symbol = serializers.CharField(source="unit.symbol", read_only=True)
    main_supplier_name = serializers.CharField(
        source="main_supplier.supplier", read_only=True,
    )

    # Campos de densidade (opcionais, só usados quando unit é de volume)
    density = serializers.DecimalField(
        max_digits=10, decimal_places=6,
        required=False, allow_null=True, write_only=True,
    )
    mass_unit = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
        required=False, allow_null=True, write_only=True,
    )
    volume_unit = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
        required=False, allow_null=True, write_only=True,
    )
    reference_temperature_celsius = serializers.DecimalField(
        max_digits=5, decimal_places=2,
        required=False, allow_null=True, write_only=True,
        default=Decimal("20"),
    )
    density_date = serializers.DateField(
        required=False, allow_null=True, write_only=True,
    )

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
            "main_supplier",
            "main_supplier_name",
            "active",
            # densidade embutida
            "density",
            "mass_unit",
            "volume_unit",
            "reference_temperature_celsius",
            "density_date",
        )

    def validate(self, attrs):
        unit = attrs.get("unit") or (self.instance.unit if self.instance else None)
        if unit is None:
            return attrs

        is_volume = unit.physical_quantity.slug == "volume"

        if is_volume:
            missing = [
                f for f in ("density", "mass_unit", "volume_unit", "density_date")
                if attrs.get(f) is None
            ]
            if missing:
                raise serializers.ValidationError({
                    f: "Obrigatório para insumo de volume."
                    for f in missing
                })

            mass_unit = attrs["mass_unit"]
            volume_unit = attrs["volume_unit"]
            if mass_unit.physical_quantity.slug != "massa":
                raise serializers.ValidationError(
                    {"mass_unit": "Deve ser uma unidade de massa."}
                )
            if volume_unit.physical_quantity.slug != "volume":
                raise serializers.ValidationError(
                    {"volume_unit": "Deve ser uma unidade de volume."}
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        density_data = self._pop_density(validated_data)
        ingredient = FoodIngredient.objects.create(**validated_data)
        if density_data:
            FoodIngredientDensity.objects.create(
                food_ingredient=ingredient, **density_data,
            )
        return ingredient

    @transaction.atomic
    def update(self, instance, validated_data):
        density_data = self._pop_density(validated_data)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        if density_data:
            FoodIngredientDensity.objects.create(
                food_ingredient=instance, **density_data,
            )
        return instance

    @staticmethod
    def _pop_density(validated_data):
        keys = (
            "density",
            "mass_unit",
            "volume_unit",
            "reference_temperature_celsius",
            "density_date",
        )
        density = {k: validated_data.pop(k) for k in keys if k in validated_data}
        if not density or density.get("density") is None:
            return None
        return {
            "density": density["density"],
            "mass_unit": density["mass_unit"],
            "volume_unit": density["volume_unit"],
            "reference_temperature_celsius": density.get(
                "reference_temperature_celsius", Decimal("20"),
            ),
            "date": density["density_date"],
        }