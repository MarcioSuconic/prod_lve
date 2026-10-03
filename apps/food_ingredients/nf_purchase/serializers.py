from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from apps.food_ingredients.food_ingredient_purchase.models import (
    FoodIngredientPurchase,
)

from .models import NFPurchase


class NFPurchaseItemSerializer(serializers.ModelSerializer):
    food_ingredient_name = serializers.CharField(
        source="food_ingredient.food_ingredient", read_only=True,
    )
    unit_symbol = serializers.CharField(source="unit.symbol", read_only=True)
    unit_price = serializers.DecimalField(
        max_digits=20, decimal_places=8, read_only=True,
    )

    class Meta:
        model = FoodIngredientPurchase
        fields = (
            "id",
            "food_ingredient",
            "food_ingredient_name",
            "quantity",
            "unit",
            "unit_symbol",
            "total_price",
            "unit_price",
        )
        read_only_fields = ("id",)

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Quantidade deve ser maior que zero."
            )
        return value

    def validate_total_price(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "Total do item não pode ser negativo."
            )
        return value


class NFPurchaseSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(
        source="supplier.supplier", read_only=True,
    )
    items = NFPurchaseItemSerializer(many=True)

    class Meta:
        model = NFPurchase
        fields = (
            "id",
            "date",
            "supplier",
            "supplier_name",
            "total_value",
            "items",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_at", "updated_at")

    def validate(self, attrs):
        items = attrs.get("items") or []
        if not items:
            raise serializers.ValidationError(
                {"items": "A NF precisa ter pelo menos um item."}
            )

        total_enviado = attrs.get("total_value")
        total_calculado = sum(
            (item["total_price"] for item in items),
            Decimal("0"),
        )
        if total_enviado != total_calculado:
            raise serializers.ValidationError({
                "total_value": (
                    f"Total da NF ({total_enviado}) não confere com a soma "
                    f"dos itens ({total_calculado})."
                ),
            })
        return attrs

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        with transaction.atomic():
            nf = NFPurchase.objects.create(**validated_data)
            for item_data in items_data:
                FoodIngredientPurchase.objects.create(
                    nf=nf,
                    date=nf.date,
                    **item_data,
                )
        return nf