# /home/marcio/Desktop/projetos/app_prod_lve/apps/products/product_production/models.py
from django.db import models
from apps.products.product.models import Product

# Create your models here.

class RegisterProductionProducts(models.Model):
    """
    Registra as produções dos produtos.

    Args:
        models (_type_): _description_
    """
    date_production = models.DateTimeField(verbose_name="Data e horário da produção de sub produtos")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name="produto")
    done = models.BooleanField(verbose_name="feito")
    class Meta:
        ordering = ['product', 'date_production','done']
        db_table = "lve_pro_register_production_product"
        verbose_name = "Registro das Produções de Produtos"
    
    def __str__(self):
        return f"{self.product} {self.date_production} {self.done}"
    
class FeedBackProductionProdcts(models.Model):
    """
    Feed Back da Produção dos Produtos.
    Servirá para referência para as construções das próximas receitas.

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    register_production_product = models.ForeignKey(RegisterProductionProducts, on_delete=models.PROTECT, verbose_name="Feed Back da Produção de Produtos.")
    feedback = models.TextField(verbose_name="Retorno da Produção de Produtos")

    def __str__(self):
        return f"{self.register_production_product}"
    class Meta:
        ordering = ['register_production_product']
        db_table = "lve_pro_feedback_production_product"
        verbose_name = 'FeedBack do registro de Produção'
        verbose_name_plural = 'FeedBacks dos Registros de Produção'
