#/home/marcio/Desktop/projetos/app_prod_lve/apps/recipe/execution_operation_base_recipe/models.py
from django.core.exceptions import ValidationError
from django.db import models

from apps.food_ingredients.food_ingredient.models import FoodIngredient
from apps.units.unit.models import Unit
from apps.recipe.base_recipe.models import BaseRecipe
from apps.recipe.stage_base_recipe.models import StageBaseRecipe
from apps.recipe.operation_base_recipe.models import OperationBaseRecipe
from apps.machinerys.machinery.models import Machinery
from apps.utensils.utensil.models import Utensil

from decimal import Decimal

class ExecutionOperationBaseRecipe(models.Model):
    
    # receita base
    base_recipe = models.ForeignKey(
        BaseRecipe,
        on_delete=models.PROTECT,
        related_name="execucoes", 
        verbose_name="receita base",
        
    )
    
    machinery = models.ForeignKey(
        Machinery,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="process_machinery",
        verbose_name="maquinário",
    )
    
    utensils = models.ForeignKey(
        Utensil,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="process_utensils",
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
    
    incorporation_percentage = models.DecimalField(
        verbose_name="percentual de incorporação do insumo no produto",
        max_digits=5,
        decimal_places=2,
        default=Decimal("100.00"),
        help_text=(
            "Quanto do insumo fica no produto final. "
            "100 = tudo incorporado; 0 = nada (ex: água de cozimento descartada); "
            "80 = 20% se perde no processo."
        ),
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
    
    temperature = models.DecimalField(verbose_name="temperatura", default=20.0, blank=False, null=False, decimal_places=2, max_digits=6)
    pH = models.DecimalField(verbose_name="pH", default=7.00, blank=False, null=False, decimal_places=2, max_digits=5)
    
    execution_time = models.DurationField(
        verbose_name="tempo de execução (min)",
        help_text="tempo em minutos",
    )

    # tempo decorrido
    elapsed_time = models.DurationField(
        verbose_name="tempo decorrido",
        help_text="tempo em minutos",
    )
    class Meta:
        ordering = ["base_recipe", "stage_execution", "operation_execution"]
        db_table = "lve_rec_execution_operation_base_recipe"
        verbose_name = "Execução da Operação da receita base"
        verbose_name_plural = "Execuções das Operações da receita base"

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