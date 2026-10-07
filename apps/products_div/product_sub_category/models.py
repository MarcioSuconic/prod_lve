#/home/marcio/Desktop/projetos/app_prod_lve/apps/products_div/product_sub_category/models.py
from django.db import models
from apps.products_div.product_category.models import ProductCategory

# Create your models here.
class ProductSubCategory(models.Model):
    category = models.ForeignKey(ProductCategory, verbose_name="categoria do produto", on_delete=models.PROTECT, blank=False, null=False)
    sub_category = models.CharField(verbose_name="sub categoria do produto", max_length=60, blank=False, null=False)
    description_menu = models.CharField(verbose_name="descrição para o menu", blank=False, null=False, max_length=120)
    
    markup_default = models.DecimalField(verbose_name="markup padrão", max_digits=8, decimal_places=4, default=200.0000, blank=False, null=False)
    
    created_at = models.DateTimeField(verbose_name="criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="atualizado em", auto_now=True)
    active = models.BooleanField(verbose_name="ativo", default=True)    
    
    class Meta:
        db_table = "lve_pdv_product_sub_category"
        ordering = ['sub_category']
        verbose_name = "Sub Categoria de Produto"
        verbose_name_plural = "Sub Categorias de Produtos"
        
    def __str__(self):
        return self.sub_category
