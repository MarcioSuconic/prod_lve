#/home/marcio/Desktop/projetos/app_prod_lve/apps/utensils/utensil/models.py
from django.db import models

from apps.units.unit.models import Unit
from apps.stories.store.models import Store


class Utensil(models.Model):
    """
    Maquinário para a feitura de produtos.
    """

    utensil = models.CharField(verbose_name="utensílios", max_length=96)

    description = models.CharField(verbose_name="descrição completa", max_length=600)

    value_utensil = models.DecimalField(
        verbose_name="valor do utensílio",
        max_digits=9,
        decimal_places=2,
    )
    code = models.CharField(
        max_length=6,
        unique=True,
        verbose_name="código operacional",
        help_text="Atalho curto para o operador localizar o utensílio. Ex.: ASS-01, BDJ-01.",
    )
    store = models.ForeignKey(
        Store,
        verbose_name="Loja",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )

    created_at = models.DateTimeField(verbose_name="criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="atualizado em", auto_now=True)
    active = models.BooleanField(verbose_name="ativo", default=True)

    class Meta:
        db_table = "lve_mac_utensil"
        verbose_name = "Utensílio"
        verbose_name_plural = "Utensílios"
        ordering = ["utensil"]
        constraints = [
            models.UniqueConstraint(
                fields=["store", "utensil"],
                name="unique_utensil_per_store",
            ),
        ]

    def __str__(self):
        return f"{self.utensil}"
