#/home/marcio/Desktop/projetos/app_prod_lve/apps/stories/electric_power_x_store/models.py

from django.db import models
from apps.stories.store.models import Store
from apps.units.unit.models import Unit

class ElectricPower_x_Store(models.Model):
    
    store = models.ForeignKey(
        Store,
        verbose_name="estabelecimento",
        on_delete=models.CASCADE,
        related_name="electric_power_fares",
    )
    
    fare_amount_kwh = models.DecimalField(
        verbose_name="valor da tarifa da energia elétrica",
        max_digits=12,
        decimal_places=4,
    )

    unit = models.ForeignKey(
        Unit,
        verbose_name="unidade da tarifa de energia elétrica",
        default=10,
        on_delete=models.PROTECT,
        limit_choices_to={"physical_quantity__slug": "tarifa-energia"},
    )

    date = models.DateField(verbose_name="data referencial")

    created_at = models.DateTimeField(
        verbose_name="criado em",
        auto_now_add=True,
    )
    
    updated_at = models.DateTimeField(
        verbose_name="atualizado em",
        auto_now=True,
    )

    class Meta:
        db_table = "lve_sto_electric_power_x_store"
        verbose_name = "Tarifa de Energia por Estabelecimento"
        verbose_name_plural = "Tarifas de Energia por Estabelecimento"
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["store", "-date"]),
            models.Index(fields=["-date"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["store", "date"],
                name="unique_fare_per_store_and_date",
            ),
            models.CheckConstraint(
                condition=models.Q(fare_amount_kwh__gte=0),
                name="fare_amount_kwh_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.store.name_store} - {self.date}"