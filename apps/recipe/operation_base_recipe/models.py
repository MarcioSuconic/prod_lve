#/home/marcio/Desktop/projetos/app_prod_lve/apps/recipe/operation_base_recipe/models.py
from django.db import models

# Create your models here.

class OperationBaseRecipe(models.Model):
    operation_base_recipe = models.CharField(max_length=60, blank=False, null=False)
    created_at = models.DateTimeField(verbose_name="criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="atualizado em", auto_now=True)
    active = models.BooleanField(verbose_name="ativo", default=True)
    class Meta:
        ordering = ["operation_base_recipe"]
        db_table = "lve_rec_process_base_recipe"
        verbose_name = "Processo da receita base"
        verbose_name_plural = "Processos da receita base"
    
    def __str__(self):
        return self.operation_base_recipe