from django.db import models

# Create your models here.
class ProductCategory(models.Model):
    category = models.CharField(verbose_name="categoria do produto", max_length=60, blank=False, null=False)
    description_menu = models.CharField(verbose_name="descrição para o menu", blank=False, null=False, max_length=120)
    
    class Meta:
        db_table = "lve_pdv_product_category"
        ordering = ['category']
        verbose_name = "Categoria de Produto"
        verbose_name_plural = "Categorias de Produtos"
        
    def __str__(self):
        return self.category
    