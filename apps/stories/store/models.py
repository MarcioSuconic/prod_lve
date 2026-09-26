#/home/marcio/Desktop/projetos/app_prod_lve/apps/stories/store/models.py

from django.db import models

# Create your models here.

class Store(models.Model):
    name_store = models.CharField(verbose_name="nome do estabelecimento", max_length=120, blank=False, null=False)
    id_store = models.IntegerField(verbose_name="ID da loja no app Principal")

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
        db_table = "lve_sto_store"
        verbose_name = "Estabelecimento"
        verbose_name_plural = "Estabelecimentos"
        ordering = ["name_store"]

    def __str__(self):
        return f"{self.name_store}"