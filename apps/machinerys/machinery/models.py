#/home/marcio/Desktop/projetos/app_prod_lve/apps/machinerys/machinery/models.py
from django.db import models

from apps.units.unit.models import Unit
from apps.stories.store.models import Store

# Create your models here.
class Machinery(models.Model):
    
    """
    Maquinário para a feitura de produtos.

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    
    machinery = models.CharField(verbose_name="maquinário", max_length=96)
    description = models.CharField(verbose_name="descrição completa", max_length=600)
    qtde_power = models.DecimalField(verbose_name="potência do maquinário", decimal_places=2, max_digits=8)
    unit_power = models.ForeignKey(Unit, verbose_name="unidade de potência", on_delete=models.PROTECT, blank=False, null=False, related_name="rel_power")
    value_machinery = models.DecimalField(verbose_name="valor do maquinário", max_digits=9, decimal_places=2)
    store = models.ForeignKey(Store, verbose_name="Loja", on_delete=models.PROTECT, blank=False, null=False)
    
    created_at = models.DateTimeField(
        verbose_name="criado em",
        auto_now_add=True,
    )
    
    updated_at = models.DateTimeField(
        verbose_name="atualizado em",
        auto_now=True,
    )
    
    active = models.BooleanField(
        verbose_name="ativo", 
        default=True
    )

    class Meta:
        db_table = "lve_mac_machinery"
        verbose_name = "Maquinário"
        verbose_name_plural = "Maquinários"
        ordering = ["machinery"]

    def __str__(self):
        return f"{self.machinery}"
    