from decimal import Decimal

from django.db import models

from apps.food_ingredients.food_ingredient.models import FoodIngredient
from apps.units.unit.models import Unit


class FoodIngredientPurchase(models.Model):
    """
    Compra de um insumo. O usuário registra o que comprou (quantidade + unidade)
    e quanto pagou no total. O preço por unidade é derivado, não digitado.
    """

    food_ingredient = models.ForeignKey(
        FoodIngredient,
        on_delete=models.PROTECT,
        related_name="purchases",
        verbose_name="insumo",
    )
    date = models.DateField(verbose_name="data da compra")
    quantity = models.DecimalField(
        verbose_name="quantidade comprada",
        max_digits=12,
        decimal_places=3,
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        verbose_name="unidade da quantidade",
    )
    total_price = models.DecimalField(
        verbose_name="valor total pago",
        max_digits=14,
        decimal_places=2,
    )

    created_at = models.DateTimeField(verbose_name="criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="atualizado em", auto_now=True)

    class Meta:
        db_table = "lve_foo_food_ingredient_purchase"
        verbose_name = "Compra de Insumo"
        verbose_name_plural = "Compras de Insumos"
        ordering = ["food_ingredient", "-date"]
        indexes = [
            models.Index(fields=["food_ingredient", "-date"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0),
                name="purchase_quantity_positive",
            ),
            models.CheckConstraint(
                condition=models.Q(total_price__gte=0),
                name="purchase_total_price_non_negative",
            ),
        ]

    @property
    def unit_price(self) -> Decimal:
        """Preço por 1 unidade da `unit` escolhida (derivado de total_price ÷ quantity)."""
        if not self.quantity:
            return Decimal("0")
        return self.total_price / self.quantity

    def __str__(self):
        return f"{self.food_ingredient} - {self.date} ({self.quantity} {self.unit.symbol})"
