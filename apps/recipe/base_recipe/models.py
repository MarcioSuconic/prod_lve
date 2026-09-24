from django.db import models
from apps.units.unit.models import Unit

# Create your models here.

class BaseRecipe(models.Model):
    base_recipe = models.CharField(verbose_name="receita base", max_length=120, blank=False, null=False)
    description = models.CharField(verbose_name="descrição da receita base", max_length=600, blank=False, null=False)
    size = models.DecimalField(verbose_name="tamanho da receita base", decimal_places=2, max_digits=9, blank=False, null=False)
    unit_size = models.ForeignKey(Unit, verbose_name="unidade do tamanho da receita base", on_delete=models.PROTECT, null=False, blank=False)
    
    class Meta:
        db_table = "lve_rec_base_recipe"
        verbose_name = "Receita Base"
        verbose_name_plural = "Receitas Base"
        ordering = ["base_recipe", "size", "unit_size"]
        
    def __str__(self):
        return self.base_recipe
    
    