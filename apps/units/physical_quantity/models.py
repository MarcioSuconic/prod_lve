from django.db import models

# Create your models here.
class PhysicalQuantity(models.Model):
    physical_quantity = models.CharField(max_length=48, verbose_name="grandeza física")
    
    class Meta:
        db_table = "lve_uni_physical_quantity"
        verbose_name = "Grandeza Física"
        verbose_name_plural = "Grandezas Físicas"
        ordering = ["physical_quantity"]
    
    def __str__(self):
        return self.physical_quantity