#/home/marcio/Desktop/projetos/app_prod_lve/apps/stories/average_hourly_wage_x_store/models.py
from django.db import models
from apps.stories.store.models import Store


class AverageHourlyWage_x_Store(models.Model):
    store = models.ForeignKey(
        Store,
        verbose_name="estabelecimento",
        on_delete=models.CASCADE,
        related_name="average_hourly_wage",
    )
    average_hourly_wage = models.DecimalField(
        verbose_name="valor médio da hora trabalhada",
        max_digits=12,
        decimal_places=4,
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
        db_table = "lve_sto_average_hourly_wage_x_store"
        verbose_name = "Valor médio da hora trabalhada por Estabelecimento"
        verbose_name_plural = "Valor médio da hora trabalhada por Estabelecimento"
        ordering = ["-date", "-created_at"]
        indexes = [
            models.Index(fields=["store", "-date"]),
            models.Index(fields=["-date"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["store", "date"],
                name="unique_avr_wage_per_store_and_date",
            ),
            models.CheckConstraint(
                condition=models.Q(average_hourly_wage__gte=0),
                name="average_hourly_wage_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.store.name_store} - {self.date}"
