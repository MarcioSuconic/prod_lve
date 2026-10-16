# apps/products/product/models.py
from django.db import models

from apps.stories.store.models import Store
from apps.products_div.product_sub_category.models import ProductSubCategory
from apps.units.unit.models import Unit


class Product(models.Model):
    """
    Registro do Produto a ser vendido no estabelecimento.
    Um produto é constituído de algum(ns) sub-produtos que são registrados
    em outra tabela.
    """

    product = models.CharField(
        verbose_name="produto", max_length=120, blank=False, null=False,
    )
    description_product = models.CharField(
        verbose_name="descrição do produto",
        blank=False, null=False, max_length=600,
    )
    name_menu = models.CharField(
        verbose_name="nome para o menu", max_length=48, blank=False, null=False,
    )
    description_menu = models.CharField(
        verbose_name="descrição do menu", max_length=120,
    )

    product_weight_or_volume = models.DecimalField(
        verbose_name="peso ou volume",
        blank=False, null=True,
        max_digits=12, decimal_places=4,
    )
    unit_weight_or_volume = models.ForeignKey(
        Unit,
        on_delete=models.PROTECT,
        verbose_name="unidade",
        blank=False, null=False,
        related_name="unit_product",
    )

    # Capacidade e produção padrão (definidos pela experiência do usuário)
    production_capacity = models.DecimalField(
        verbose_name="capacidade de produção",
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text=(
            "Quantas unidades o usuário consegue fazer por batida. "
            "Definido pela experiência, ajustado com o tempo."
        ),
    )
    default_production = models.DecimalField(
        verbose_name="produção padrão",
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
        help_text=(
            "Quantidade sugerida por batida. "
            "Preenchida automaticamente ao adicionar o produto à produção."
        ),
    )

    store = models.ForeignKey(
        Store,
        on_delete=models.PROTECT,
        blank=False, null=False,
        related_name="product_store",
        verbose_name="Loja",
    )

    sub_category = models.ForeignKey(
        ProductSubCategory,
        on_delete=models.PROTECT,
        blank=False, null=False,
    )
    created_at = models.DateTimeField(verbose_name="criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="atualizado em", auto_now=True)
    active = models.BooleanField(verbose_name="ativo", default=True)

    class Meta:
        db_table = "lve_pro_products"
        ordering = ["product"]
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        constraints = [
            models.UniqueConstraint(
                fields=["store", "product"],
                name="unique_product_per_store",
            ),
        ]

    def __str__(self):
        return self.product