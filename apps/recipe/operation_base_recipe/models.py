# apps/recipe/operation_base_recipe/models.py
from decimal import Decimal

from django.db import models


class OperationBaseRecipe(models.Model):
    operation_base_recipe = models.CharField(max_length=60, blank=False, null=False)
    description = models.CharField(
        verbose_name="descrição da operação",
        max_length=240,
        blank=True,
        null=True,
    )
    labor_minutes = models.DecimalField(
        verbose_name="tempo de mão de obra (min)",
        max_digits=6,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text=(
            "Tempo que o operador dedica à operação. "
            "Pode ser diferente do tempo de execução "
            "(ex: forno ligado 60 min, mas só 1 min de mão de obra)."
        ),
    )
    created_at = models.DateTimeField(verbose_name="criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="atualizado em", auto_now=True)
    active = models.BooleanField(verbose_name="ativo", default=True)

    class Meta:
        ordering = ["operation_base_recipe"]
        db_table = "lve_rec_operation_base_recipe"
        verbose_name = "Operação da receita base"
        verbose_name_plural = "Operação da receita base"

    def __str__(self):
        return self.operation_base_recipe