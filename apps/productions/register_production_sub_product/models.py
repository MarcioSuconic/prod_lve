# /home/marcio/Desktop/projetos/app_prod_lve/apps/productions/register_production_sub_product/models.py
from django.db import models
from apps.sub_products.sub_product.models import SubProduct

# Create your models here.

class RegisterProductionSubProducts(models.Model):
    """
    Registra as produções dos Sub_produtos.

    Args:
        models (_type_): _description_
    """
    date_production = models.DateTimeField(verbose_name="Data e horário da produção de sub produtos")
    sub_product = models.ForeignKey(SubProduct, on_delete=models.PROTECT, verbose_name="sub produto")
    done = models.BooleanField(verbose_name="feito")
    
    
    class Meta:
        ordering = ['sub_product', 'date_production','done']
        db_table = "lve_pro_register_production_sub_product"
        verbose_name = "Registro das Produções de Sub produtos"
    
    def __str__(self):
        return f"{self.sub_product} {self.date_production} {self.done}"
    
class FeedBackProductionSubProdcts(models.Model):
    """
    Feed Back da Produção dos Sub produtos.
    Servirá para referência para as construções das próximas receitas.

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    register_production_sub_product = models.ForeignKey(RegisterProductionSubProducts, on_delete=models.PROTECT, verbose_name="Feed Back da Produção de Sub Produtos.")
    feedback = models.TextField(verbose_name="Retorno da Produção de Sub produtos")

    def __str__(self):
        return f"{self.register_production_sub_product}"

    class Meta:
        ordering = ['register_production_sub_product']
        db_table = "lve_pro_feedback_production_sub_product"
        verbose_name = 'FeedBack do registro de Produção'
        verbose_name_plural = 'FeedBacks dos Registros de Produção'