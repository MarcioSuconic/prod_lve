# /home/marcio/Desktop/projetos/app_prod_lve/apps/productions/register_production_sub_product/models.py
from django.db import models
from apps.sub_products.sub_product.models import SubProduct
from apps.units.unit.models import Unit   # adicione no topo
from apps.stories.store.models import Store  

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
    store = models.ForeignKey(
        Store,
        verbose_name="estabelecimento",
        on_delete=models.PROTECT,
    )
    quantity = models.DecimalField(
        verbose_name="quantidade produzida",
        max_digits=10,
        decimal_places=3,
    )
    unit = models.ForeignKey(
        Unit,
        verbose_name="unidade da quantidade produzida",
        on_delete=models.PROTECT,
    )
    
    
    class Meta:
        ordering = ["store", "sub_product", "date_production", "done"]
        db_table = "lve_pdc_production_sub_product"
        verbose_name = "Registro da Produção de Sub produto"
        verbose_name_plural = "Registros das Produções de Sub produtos"
    
    def __str__(self):
        return f"{self.sub_product} {self.date_production} {self.done}"
    
class FeedBackProductionSubProducts(models.Model):       # corrigido
    register_production_sub_product = models.ForeignKey(
        RegisterProductionSubProducts,
        on_delete=models.PROTECT,
        verbose_name="Feed Back da Produção de Sub Produtos.",
    )
    feedback = models.TextField(verbose_name="Retorno da Produção de Sub produtos")

    def __str__(self):
        return f"{self.register_production_sub_product}"
    class Meta:
        ordering = ["register_production_sub_product"]
        db_table = "lve_pdc_feedback_production_sub_product"
        verbose_name = "FeedBack do registro de Produção"
        verbose_name_plural = "FeedBacks dos Registros de Produção"