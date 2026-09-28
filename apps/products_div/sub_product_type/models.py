# /home/marcio/Desktop/projetos/app_prod_lve/apps/products_div/sub_product_type/models.py
from django.db import models

# Create your models here.
class SubProductType(models.Model):
    sub_product_type = models.CharField(verbose_name="Tipo do sub produto", max_length=60, blank=False, null=False)
    created_at = models.DateTimeField(verbose_name="criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="atualizado em", auto_now=True)
    active = models.BooleanField(verbose_name="ativo", default=True)
    
    class Meta:
        db_table = "lve_pdv_sub_product_type"
        ordering = ['sub_product_type']
        verbose_name = "Tipo de Sub Produto"
        verbose_name_plural = "Tipos de Sub Produtos"
        
    def __str__(self):
        return self.sub_product_type
