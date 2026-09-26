from django.db import models

# Create your models here.

class StageBaseRecipe(models.Model):
    stage_base_recipe = models.CharField(max_length=60, blank=False, null=False)
    
    class Meta:
        ordering = ["stage_base_recipe"]
        db_table = "lve_rec_stage_base_recipe"
        verbose_name = "Etapa da receita base"
        verbose_name_plural = "Etapas da receita base"
    
    def __str__(self):
        return self.stage_base_recipe