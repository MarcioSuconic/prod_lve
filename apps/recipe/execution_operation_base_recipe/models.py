from django.core.exceptions import ValidationError
from django.db import models

from apps.food_ingredients.food_ingredient.models import FoodIngredient
from apps.units.unit.models import Unit
from apps.recipe.base_recipe.models import BaseRecipe
from apps.recipe.stage_base_recipe.models import StageBaseRecipe
from apps.recipe.operation_base_recipe.models import OperationBaseRecipe
from apps.machinerys.machinery.models import Machinery, Utensil

class ExecutionOperationBaseRecipe(models.Model):
    # receita base
    base_recipe = models.ForeignKey(
        BaseRecipe,
        on_delete=models.PROTECT,
        verbose_name="receita base",
    )
    
    machinery = models.ForeignKey(
        Machinery,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="process_steps",
        verbose_name="maquinário",
    )
    
    utensils = models.ManyToManyField(
        Utensil,
        blank=True,
        related_name="process_steps",
        verbose_name="utensílios",
    )

    # descrição da execução do processo
    description_execution = models.CharField(
        max_length=240,
        verbose_name="descrição da execução",
    )

    # insumo (opcional — nem todo passo usa insumo)
    food_ingredient = models.ForeignKey(
        FoodIngredient,
        verbose_name="insumo",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    qtde_food_ingredient = models.DecimalField(
        verbose_name="qtde insumo",
        max_digits=10,
        decimal_places=3,
        blank=True,
        null=True,
    )
    unidade_qtde_food_ingredient = models.ForeignKey(
        Unit,
        verbose_name="unidade da qtde de insumo",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
    )
    unincorporated_ingredient = models.BooleanField(
        verbose_name="ingrediente não incorporado no peso total",
        default=False,
    )

    # etapa da execução
    stage_execution = models.ForeignKey(
        StageBaseRecipe,
        on_delete=models.PROTECT,
        verbose_name="etapa da execução do produto",
    )

    # processo da execução
    operation_execution = models.ForeignKey(
        OperationBaseRecipe,
        on_delete=models.PROTECT,
        verbose_name="operação da execução",
    )

    # tempo decorrido
    elapsed_time = models.DurationField(
        verbose_name="tempo decorrido",
    )

    class Meta:
        ordering = ["base_recipe", "stage_execution", "operation_execution"]
        db_table = "lve_rec_execution_operation_base_recipe"          # era process
        verbose_name = "Execução da Operação da receita base"          # era Processo
        verbose_name_plural = "Execuções das Operações da receita base"  # era Processos

    def clean(self):
        """
        Garante que os campos de insumo sejam preenchidos em conjunto.
        Ou os três estão preenchidos, ou nenhum está.
        """
        insumo_preenchido = [
            self.food_ingredient is not None,
            self.qtde_food_ingredient is not None,
            self.unidade_qtde_food_ingredient is not None,
        ]
        if any(insumo_preenchido) and not all(insumo_preenchido):
            raise ValidationError(
                "Se um passo usa insumo, os três campos "
                "(insumo, quantidade e unidade) devem ser preenchidos."
            )

    def __str__(self):
        return f"{self.base_recipe} - {self.stage_execution} - {self.operation_execution}"