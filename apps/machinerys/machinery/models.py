from django.db import models

from apps.units.unit.models import Unit
from apps.stories.store.models import Store


class Machinery(models.Model):
    """
    Maquinário para a feitura de produtos.
    """

    machinery = models.CharField(verbose_name="maquinário", max_length=96)
    description = models.CharField(verbose_name="descrição completa", max_length=600)
    qtde_power = models.DecimalField(
        verbose_name="potência do maquinário",
        decimal_places=2,
        max_digits=8,
    )
    unit_power = models.ForeignKey(
        Unit,
        verbose_name="unidade de potência",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        related_name="rel_power",
    )
    value_machinery = models.DecimalField(
        verbose_name="valor do maquinário",
        max_digits=9,
        decimal_places=2,
    )
    code = models.CharField(
        max_length=6,
        unique=True,
        verbose_name="código operacional",
        help_text="Atalho curto para o operador localizar o maquinário. Ex.: FOR-01, MAS-01.",
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
        db_table = "lve_mac_machinery"
        verbose_name = "Maquinário"
        verbose_name_plural = "Maquinários"
        ordering = ["machinery"]
        constraints = [
            models.UniqueConstraint(
                fields=["store", "machinery"],
                name="unique_machinery_per_store",
            ),
        ]

    def __str__(self):
        return f"{self.machinery}"
