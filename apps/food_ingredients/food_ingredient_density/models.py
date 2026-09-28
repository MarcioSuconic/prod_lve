#/home/marcio/Desktop/projetos/app_prod_lve/apps/food_ingredients/food_ingredient_density/models.py

from django.db import models

from apps.food_ingredients.food_ingredient.models import FoodIngredient
from apps.units.unit.models import Unit


class FoodIngredientDensity(models.Model):
    """
    Densidade de um insumo, com histórico.

    Cada linha representa uma medição de densidade para um insumo, em uma
    temperatura de referência, em uma data. Para converter massa <-> volume
    de um insumo, use a medição mais recente (ou a mais próxima da
    temperatura de trabalho).

    Args:
        mass_unit e volume_unit são explícitos porque a densidade só tem
        significado se as unidades de massa e volume forem declaradas
        (ex.: 1.0300 kg/L é diferente de 1.0300 g/mL, embora o número
        pareça o mesmo).
    """

    food_ingredient = models.ForeignKey(
        FoodIngredient,
        on_delete=models.PROTECT,
        related_name="densities",
        verbose_name="insumo",
    )
    density = models.DecimalField(
        verbose_name="densidade",
        max_digits=10,
        decimal_places=6,
    )
    mass_unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="densities_as_mass",
        limit_choices_to={"physical_quantity__slug": "massa"},
        verbose_name="unidade de massa",
    )
    volume_unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        related_name="densities_as_volume",
        limit_choices_to={"physical_quantity__slug": "volume"},
        verbose_name="unidade de volume",
    )
    reference_temperature_celsius = models.DecimalField(
        verbose_name="temperatura de referência (°C)",
        max_digits=5,
        decimal_places=2,
        default=20,
    )
    date = models.DateField(verbose_name="data da medição")

    created_at = models.DateTimeField(verbose_name="criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="atualizado em", auto_now=True)

    class Meta:
        db_table = "lve_foo_food_ingredient_density"
        verbose_name = "Densidade de Insumo"
        verbose_name_plural = "Densidades de Insumos"
        ordering = ["food_ingredient", "-date"]
        indexes = [
            models.Index(fields=["food_ingredient", "-date"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(density__gt=0),
                name="food_ingredient_density_positive",
            ),
            models.UniqueConstraint(
                fields=["food_ingredient", "reference_temperature_celsius", "date"],
                name="unique_density_per_ingredient_temp_date",
            ),
        ]

    def __str__(self):
        return (
            f"{self.food_ingredient} @ {self.reference_temperature_celsius}°C "
            f"({self.density} {self.mass_unit.symbol}/{self.volume_unit.symbol})"
        )
