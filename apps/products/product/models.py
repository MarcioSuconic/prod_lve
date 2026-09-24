from django.db import models
from apps.stories.store.models import Store
from apps.products_div.product_sub_category.models import ProductSubCategory

# Create your models here.

class Product(models.Model):
    product = models.CharField(verbose_name="produto", max_length=120, blank=False, null=False)
    description_product = models.CharField(verbose_name="descrição do produto", blank=False, null=False, max_length=600)
    name_menu = models.CharField(verbose_name="nome para o menu", max_length=48, blank=False, null=False)
    description_menu = models.CharField(verbose_name="descrição do menu", max_length=120)
    store = models.ForeignKey(Store, on_delete=models.PROTECT, blank=False, null=False)
    sub_category = models.ForeignKey(ProductSubCategory, on_delete=models.PROTECT, blank=False, null=False)
    
    class Meta:
        db_table = "lve_pro_products"
        ordering = ["product"]
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        
    def __str__(self):
        return self.product
