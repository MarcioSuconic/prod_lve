# apps/productions/production_input/models.py
from django.db import models

from apps.food_ingredients.food_ingredient.models import FoodIngredient
from apps.productions.sub_product_production.models import (
    RegisterProductionSubProducts,
)
from apps.units.unit.models import Unit


class ProductionInput(models.Model):
    """
    Registra o INPUT real de uma produção de sub-produto.

    Cada linha = um insumo que entrou na produção, com quantidade e unidade.
    Usado pra comparar com o esperado (da receita) e calibrar o
    incorporation_percentage ao longo do tempo.
    """
    register_production_sub_product = models.ForeignKey(
        RegisterProductionSubProducts,
        on_delete=models.CASCADE,
        related_name="inputs",
        verbose_name="registro de produção",
    )
    food_ingredient = models.ForeignKey(
        FoodIngredient,
        on_delete=models.PROTECT,
        verbose_name="insumo",
    )
    quantity = models.DecimalField(
        verbose_name="quantidade",
        max_digits=12,
        decimal_places=3,
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        verbose_name="unidade",
    )
    cost = models.DecimalField(
        verbose_name="custo real pago",
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Opcional. Se não informado, usa o preço da última compra.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "lve_pdc_production_input"
        verbose_name = "Insumo da Produção"
        verbose_name_plural = "Insumos da Produção"
        ordering = ["register_production_sub_product", "food_ingredient"]
        constraints = [
            models.UniqueConstraint(
                fields=["register_production_sub_product", "food_ingredient"],
                name="unique_input_per_production_and_ingredient",
            ),
        ]

    def __str__(self):
        return (
            f"{self.register_production_sub_product} — "
            f"{self.food_ingredient} ({self.quantity} {self.unit.symbol})"
        )
