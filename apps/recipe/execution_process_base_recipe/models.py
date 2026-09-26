#/home/marcio/Desktop/projetos/app_prod_lve/apps/recipe/execution_process_base_recipe/models.py
from django.db import models
from apps.food_ingredients.food_ingredient.models import FoodIngredient
from apps.units.unit.models import Unit
from apps.recipe.base_recipe.models import BaseRecipe
from apps.recipe.stage_base_recipe.models import StageBaseRecipe
from apps.recipe.process_base_recipe.models import ProcessBaseRecipe

# Create your models here.

class ExecutionProcessBaseRecipe(models.Model):
    # receita base
    base_recipe = models.ForeignKey(BaseRecipe, on_delete=models.PROTECT, verbose_name="receita base")
    
    # descricao da execução do processo
    description_execution = models.CharField(max_length=240, blank=False, null=False, verbose_name="descrição da execução")
    
    #ingrediente
    food_ingredient = models.ForeignKey(FoodIngredient, verbose_name="insumo", blank=False, null=False, on_delete=models.PROTECT)
    qtde_food_ingredient = models.IntegerField(verbose_name="qtde insumo")
    unidade_qtde_food_ingredient = models.ForeignKey(Unit, verbose_name="unidade da qtde de insumo", on_delete=models.PROTECT)
    unincorporated_ingredient = models.BooleanField(verbose_name="ingrediente não incorporado no peso total", default=False, null=False)
    
    # Etapa da feitura
    stage_execution = models.ForeignKey(StageBaseRecipe, on_delete=models.PROTECT, verbose_name="Etapa da execução do produto")
    
    # Processo da Execução
    process_execution = models.ForeignKey(ProcessBaseRecipe, on_delete=models.PROTECT, verbose_name="processo da execução")
    
    # tempo decorrido
    elapsed_time = models.TimeField(verbose_name="tempo decorrido", blank=False, null=False)
    
    class Meta:
        ordering = ["base_recipe","stage_execution","process_execution"]
        db_table = "lve_rec_execution_process_base_recipe"
        verbose_name = "Execução do Processo da receita base"
        verbose_name_plural = "Execução do Processos da receita base"
    
    def __str__(self):
        return f"{self.base_recipe} - {self.stage_execution} - {self.process_execution}"