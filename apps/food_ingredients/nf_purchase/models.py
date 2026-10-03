from django.db import models
from apps.food_ingredients.supplier_food_ingredients.models import SupplierFoodIngredients

class NFPurchase(models.Model):
    date = models.DateField(verbose_name="data da NF")
    supplier = models.ForeignKey(
        SupplierFoodIngredients,
        on_delete=models.PROTECT,
        verbose_name="Fornecedor",
        blank=True,
        null=True,
    )
    total_value = models.DecimalField(
        verbose_name="total da NF",
        max_digits=14,
        decimal_places=2,
    )

    created_at = models.DateTimeField(verbose_name="criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="atualizado em", auto_now=True)

    class Meta:
        db_table = "lve_foo_nf"
        verbose_name = "Nota Fiscal"
        verbose_name_plural = "Notas Fiscais"
        ordering = ["-date"]

    def __str__(self):
        fornecedor = self.supplier.supplier if self.supplier else "sem fornecedor"
        return f"{self.date} - {fornecedor}"
    