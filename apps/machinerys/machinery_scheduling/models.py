#/home/marcio/Desktop/projetos/app_prod_lve/apps/machinerys/machinery_scheduling/models.py
from django.db import models
from apps.machinerys.machinery.models import Machinery
# Create your models here.

class MachineryScheduling(models.Model):
    """
    Agendamento do Maquinário para a feitura de produtos.
    Agendaemnto se deve para ver a ocupação do maquinário no espaço-tempo

    Args:
        models (_type_): _description_

    Returns:
        _type_: _description_
    """
    machinery = models.ForeignKey(Machinery, verbose_name="maquinário", on_delete=models.PROTECT, blank=False, null=False)
    datetime_initial = models.DateTimeField(verbose_name="Data e horário inicial")
    datetime_finish = models.DateTimeField(verbose_name="Data e horário final")

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
        db_table = "lve_mac_machinery_scheduling"
        verbose_name = "Agendamento de Maquinário"
        verbose_name_plural = "Agendamento de Maquinários"
        ordering = ["datetime_initial","datetime_finish","machinery"]

    def __str__(self):
        return f"{self.datetime_initial}-{self.datetime_finish} --> {self.machinery}"
    
