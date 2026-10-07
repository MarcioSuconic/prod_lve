# /home/marcio/Desktop/projetos/app_prod_lve/apps/products/product_x_sub_product/models.py
from django.db import models
from apps.sub_products.sub_product.models import SubProduct
from apps.products.product.models import Product


# Create your models here.
class Product_x_Sub_Product(models.Model):
    """
    Produtos x Sub Produtos.
    Registra os Sub Produtos com seu 
    respectivo percentual que integram os Produtos

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    product = models.ForeignKey(Product, verbose_name="Produto", on_delete=models.PROTECT, null=False, blank=False)
    sub_product = models.ForeignKey(SubProduct, verbose_name="Sub Produto", on_delete=models.PROTECT, null=False, blank=False)
    composition_percentage = models.DecimalField(verbose_name="percentual do padeiro", max_digits=10, decimal_places=6)
    created_at = models.DateTimeField(verbose_name="criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="atualizado em", auto_now=True)
    active = models.BooleanField(verbose_name="ativo", default=True)    
    class Meta:
        ordering = ["product", "sub_product", "composition_percentage"]
        db_table = "lve_pro_product_x_sub_product"          # corrigido
        verbose_name = "Produto X Sub-Produto"
        verbose_name_plural = "Produtos X Sub-Produtos"

    def __str__(self):
        return f"{self.product} {self.sub_product} {self.composition_percentage}"
    