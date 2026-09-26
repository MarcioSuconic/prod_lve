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
    bakers_percentage = models.DecimalField(verbose_name="percentual do padeiro", max_digits=6, decimal_places=2)
    
    class Meta:
        ordering = ["product","sub_product", "bakers_percentage"]
        db_table = "lve_pro_prduct_x_sub_product"
        verbose_name = "Produto x Sub-Produto"
        verbose_name_plural = "Produtos X Sub-Produtos"
    
    def __str__(self):
        return f"{self.product} {self.sub_product} {self.bakers_percentage}"
    