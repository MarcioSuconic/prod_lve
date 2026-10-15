# apps/productions/pending_production/models.py
from django.db import models

from apps.stories.store.models import Store
from apps.productions.sub_product_production.models import (
    RegisterProductionSubProducts,
)
from apps.productions.product_production.models import (
    RegisterProductionProducts,
)


class PendingProduction(models.Model):
    """
    Uma 'intenção' de produção.

    Agrupa N produtos + quantidades. Pode ser:
      - pending:     lista de espera (não planejada)
      - scheduled:   data/hora definida, plano calculado
      - in_progress: começou a produzir
      - done:        terminou
      - cancelled:   desistiu

    Quando executada, gera:
      - N RegisterProductionSubProducts (sub-produtos produzidos)
      - N RegisterProductionProducts (produtos produzidos)
    """

    STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("scheduled", "Planejada"),
        ("in_progress", "Em produção"),
        ("done", "Produzido"),
        ("cancelled", "Cancelado"),
    ]

    store = models.ForeignKey(
        Store,
        on_delete=models.PROTECT,
        verbose_name="estabelecimento",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="status",
    )
    scheduled_start = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="início planejado",
    )
    scheduled_end = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="fim planejado (calculado)",
    )
    # Plano calculado (sub-produtos consolidados, cronograma, custo,
    # lista de compras). Preenchido quando status vira 'scheduled'.
    plan = models.JSONField(
        null=True,
        blank=True,
        verbose_name="plano calculado",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="observações",
    )

    # Registros gerados quando executada
    register_products = models.ManyToManyField(
        RegisterProductionProducts,
        blank=True,
        related_name="pending_productions",
        verbose_name="registros de produtos produzidos",
    )
    register_sub_products = models.ManyToManyField(
        RegisterProductionSubProducts,
        blank=True,
        related_name="pending_productions",
        verbose_name="registros de sub-produtos produzidos",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lve_pdc_pending_production"
        verbose_name = "Produção Pendente"
        verbose_name_plural = "Produções Pendentes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.id} {self.store} [{self.status}] {self.created_at:%d/%m %H:%M}"