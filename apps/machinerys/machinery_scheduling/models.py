from django.db import models

from apps.machinerys.machinery.models import Machinery
from apps.productions.sub_product_production.models import (
    RegisterProductionSubProducts,
)


class MachineryScheduling(models.Model):
    """
    Agendamento do Maquinário para a feitura de sub produtos.

    Cada linha representa a reserva de um maquinário por um intervalo de tempo.
    Uma mesma execução de produção pode ter várias linhas (uma por maquinário
    utilizado), todas apontando para o mesmo RegisterProductionSubProducts.
    """

    machinery = models.ForeignKey(
        Machinery,
        verbose_name="maquinário",
        on_delete=models.PROTECT,
        blank=False,
        null=False,
    )
    datetime_initial = models.DateTimeField(verbose_name="data e horário inicial")
    datetime_finish = models.DateTimeField(verbose_name="data e horário final")

    register_production_sub_product = models.ForeignKey(
        RegisterProductionSubProducts,
        verbose_name="execução de produção do sub produto",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="machinery_schedules",
    )

    created_at = models.DateTimeField(verbose_name="criado em", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="atualizado em", auto_now=True)
    active = models.BooleanField(verbose_name="ativo", default=True)

    class Meta:
        db_table = "lve_mac_machinery_scheduling"
        verbose_name = "Agendamento de Maquinário"
        verbose_name_plural = "Agendamento de Maquinários"
        ordering = ["datetime_initial", "datetime_finish", "machinery"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(datetime_finish__gt=models.F("datetime_initial")),
                name="machinery_scheduling_finish_after_start",
            ),
        ]

    def __str__(self):
        return f"{self.datetime_initial}-{self.datetime_finish} --> {self.machinery}"