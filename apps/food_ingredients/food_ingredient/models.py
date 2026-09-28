#/home/marcio/Desktop/projetos/app_prod_lve/apps/food_ingredients/food_ingredient/models.py
from django.db import models
from apps.units.unit.models import Unit
from apps.food_ingredients.supplier_food_ingredients.models import SupplierFoodIngredients

# Create your models here.

class FoodIngredient(models.Model):
    """
    Ingredientes para ser inclusa na receita.
    
    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    food_ingredient = models.CharField(verbose_name="insumos", max_length=120, blank=False, null=False)
    description = models.CharField(verbose_name="descrição minuciosa do insumo", max_length=600, blank=False, null=False)
    qtde_default_shopping = models.DecimalField(verbose_name="qtde padrão para compra", max_digits=8, decimal_places=2)
    unit = models.ForeignKey(Unit, verbose_name="unidade", on_delete=models.PROTECT, blank=False, null=False)
    supplier = models.ForeignKey(SupplierFoodIngredients, verbose_name="Fornecedor de Insumo", on_delete=models.PROTECT, blank=False, null=False)
    
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
        db_table = "lve_foo_food_ingredients"
        verbose_name = "Insumo"
        verbose_name_plural = "Insumos"
        ordering = ['food_ingredient']
        
    def __str__(self):
        return self.food_ingredient