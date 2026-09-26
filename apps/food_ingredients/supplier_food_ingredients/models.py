from django.db import models

# Create your models here.
class SupplierFoodIngrdients(models.Model):
    """
    Fornecedores de insumos para a produção de produtos

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    supplier = models.CharField(verbose_name="Fornecedor de Insumos", max_length=60, blank=False, null=False)
    
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
        db_table = "lve_ins_fornecedores_insumos"
        verbose_name = "Fornecedor de Insumo"
        verbose_name_plural = "Fornecedores de Insumos"
        ordering = ['supplier']
        
    def __str__(self):
        return self.supplier