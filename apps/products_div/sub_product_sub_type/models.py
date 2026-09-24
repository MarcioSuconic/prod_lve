from django.db import models
from apps.products_div.sub_product_type.models import SubProductType


# Create your models here.
class SubProductSubType(models.Model):
    sub_product_sub_type = models.CharField(verbose_name="Sub tipo do sub produto", max_length=60, blank=False, null=False)
    type = models.ForeignKey(SubProductType, on_delete=models.PROTECT, blank=False, null=False)
    
    class Meta:
        db_table = "lve_pdv_sub_product_sub_type"
        ordering = ['sub_product_sub_type']
        verbose_name = "Sub Tipo de Sub Produto"
        verbose_name_plural = "Sub tipos de Sub Produtos"
        
    def __str__(self):
        return self.sub_type
