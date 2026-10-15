# apps/productions/production_x_product/models.py
from django.db import models

from apps.products.product.models import Product
from apps.units.unit.models import Unit
from apps.productions.pending_production.models import PendingProduction


class ProductionXProduct(models.Model):
    """
    Um item de uma produção: produto + quantidade + unidade.

    Um PendingProduction tem N ProductionXProduct.
    """

    production = models.ForeignKey(
        PendingProduction,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="produção",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name="produto",
    )
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        verbose_name="quantidade",
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        verbose_name="unidade",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True, verbose_name="ativo")

    class Meta:
        db_table = "lve_pdc_production_x_product"
        verbose_name = "Produção x Produto"
        verbose_name_plural = "Produções x Produtos"
        ordering = ["production", "product"]
        constraints = [
            models.UniqueConstraint(
                fields=["production", "product", "unit"],
                name="unique_product_per_production_and_unit",
            ),
        ]

    def __str__(self):
        return (
            f"{self.production} — {self.product} "
            f"({self.quantity} {self.unit.symbol})"
        )
