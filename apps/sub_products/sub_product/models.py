#/home/marcio/Desktop/projetos/app_prod_lve/apps/sub_products/sub_product/models.py
from django.db import models
from apps.products_div.sub_product_sub_type.models import SubProductSubType
from apps.recipe.base_recipe.models import BaseRecipe

# Create your models here.

class SubProduct(models.Model):
    """
    Sub Produto de um Produto.
    Um sub produto tem que ter um Produto. O produto pode ter vários ou um sub-produto.
    Cada Sub Produto tem uma receita base que será usada proporcioanalmente quando
    na produção de um Produto.

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    sub_product = models.CharField(max_length=60, verbose_name="Sub Produto")
    base_recipe = models.ForeignKey(BaseRecipe, on_delete=models.PROTECT, verbose_name="receita base")
    sub_product_sub_type = models.ForeignKey(SubProductSubType, on_delete=models.PROTECT, verbose_name="Sub Tipo do Sub Produto")
    
    def __str__(self):
        return self.sub_product