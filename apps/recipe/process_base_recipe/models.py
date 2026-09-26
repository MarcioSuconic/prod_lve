from django.db import models

# Create your models here.

class ProcessBaseRecipe(models.Model):
    process_base_recipe = models.CharField(max_length=60, blank=False, null=False)
    
    class Meta:
        ordering = ["process_base_recipe"]
        db_table = "lve_rec_process_base_recipe"
        verbose_name = "Processo da receita base"
        verbose_name_plural = "Processos da receita base"
    
    def __str__(self):
        return self.process_base_recipe