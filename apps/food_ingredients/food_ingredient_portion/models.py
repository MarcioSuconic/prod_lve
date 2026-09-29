from django.db import models

from apps.food_ingredients.food_ingredient.models import FoodIngredient
from apps.units.unit.models import Unit


class FoodIngredientPortion(models.Model):
    """
    Quantidade de referência de UMA unidade de contagem de um insumo.

    Ex.: 1 ovo = 55 g, 1 fatia de pão = 30 g, 1 lata de leite = 350 ml.

    Semântica: 1 <unit> = <reference_quantity> <reference_unit>
    """

    food_ingredient = models.ForeignKey(
        FoodIngredient,
        on_delete=models.PROTECT,
        related_name="portions",
        verbose_name="insumo",
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="portions_as_count",
        limit_choices_to={"physical_quantity__slug": "unidade"},
        verbose_name="unidade de contagem",
    )
    reference_quantity = models.DecimalField(
        verbose_name="quantidade por unidade",
        max_digits=12,
        decimal_places=3,
    )
    reference_unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="portions_as_reference",
        verbose_name="unidade de referência",
    )
    date = models.DateField(verbose_name="data da medição")

    created_at = models.DateTimeField(verbose_name="criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="atualizado em", auto_now=True)

    class Meta:
        db_table = "lve_foo_food_ingredient_portion"
        verbose_name = "Porção de Insumo"
        verbose_name_plural = "Porções de Insumos"
        ordering = ["food_ingredient", "-date"]
        indexes = [
            models.Index(fields=["food_ingredient", "-date"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(reference_quantity__gt=0),
                name="food_ingredient_portion_positive",
            ),
            models.UniqueConstraint(
                fields=["food_ingredient", "unit", "date"],
                name="unique_portion_per_ingredient_unit_date",
            ),
        ]

    def __str__(self):
        return (
            f"1 {self.unit.symbol} de {self.food_ingredient} = "
            f"{self.reference_quantity} {self.reference_unit.symbol}"
        )